"""Durable GitHub release storage, deployment decisions, and deduplicated alerts."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from scripts.http_json import fetch_json
import zipfile

RELEASE = "chirps-monthly-v1"
TITLE = "Monthly rainfall update needs attention"


def gh(*args, capture=True):
    return subprocess.run(["gh", *args], check=True, text=True, capture_output=capture).stdout


def release_assets():
    # The collection distinguishes absence from authentication/network errors.
    releases = json.loads(gh("api", f"repos/{os.environ['GH_REPO']}/releases", "--paginate", "--slurp"))
    for page in releases:
        for release in page:
            if release["tag_name"] == RELEASE:
                pages = json.loads(gh("api", f"repos/{os.environ['GH_REPO']}/releases/{release['id']}/assets", "--paginate", "--slurp"))
                return [asset for page in pages for asset in page]
    gh("release", "create", RELEASE, "--title", "CHIRPS Final monthly reductions v1", "--notes",
       "Validated complete monthly Madagascar reductions and immutable publication snapshots. SHA-256 checksums accompany every monthly reduction.")
    return []


def restore(cache):
    cache.mkdir(parents=True, exist_ok=True)
    assets = release_assets()
    names = [asset['name'] for asset in assets if asset['name'].startswith('chirps-month-') and asset['name'].endswith('.zip')]
    if names:
        gh("release", "download", RELEASE, "-p", "chirps-month-*.zip", "-D", str(cache))
    for name in names:
        with zipfile.ZipFile(cache / name) as bundle:
            for item in bundle.namelist():
                if Path(item).name != item:
                    raise ValueError("unexpected archive path")
            bundle.extractall(cache)


def snapshot():
    summary = json.loads(Path('update-summary.json').read_text())
    release = summary['release']
    filename = f'recent-release-{release}.tar.gz'
    with tempfile.TemporaryDirectory() as temporary:
        archive = Path(temporary) / filename
        # Stable archive metadata permits exact verification on no-op reruns.
        tar = subprocess.Popen(['tar', '--sort=name', '--mtime=1970-01-01', '--owner=0', '--group=0', '--numeric-owner', '-cf', '-',
                                'data/manifest.json', 'data/update-status.json', f'data/recent-rainfall/releases/{release}'], stdout=subprocess.PIPE)
        with archive.open('wb') as output:
            subprocess.run(['gzip', '-n'], stdin=tar.stdout, stdout=output, check=True)
        tar.stdout.close()
        if tar.wait() != 0:
            raise ValueError('snapshot tar failed')
        checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
        assets = release_assets()
        if filename not in [asset['name'] for asset in assets]:
            sidecar = archive.with_suffix(archive.suffix + '.sha256')
            sidecar.write_text(f'{checksum}  {filename}\n')
            gh('release', 'upload', RELEASE, str(archive), str(sidecar))
        destination = Path(temporary) / 'verified'
        destination.mkdir()
        gh('release', 'download', RELEASE, '-p', filename, '-D', str(destination))
        if hashlib.sha256((destination / filename).read_bytes()).hexdigest() != checksum:
            raise ValueError('durable publication snapshot checksum mismatch')
        print(f'preserved {filename}: {checksum}')


def decide():
    changed = bool(subprocess.run(['git', 'status', '--porcelain', '--', 'data'], check=True, capture_output=True, text=True).stdout.strip())
    if changed:
        print('publish=true')
        return
    candidate = json.loads(Path('data/update-status.json').read_text())
    try:
        live = fetch_json(os.environ['PRODUCTION_URL'] + '/data/update-status.json')
    except json.JSONDecodeError:
        # Before this feature exists, the SPA returns HTML for the new endpoint.
        live = {}
    print('publish=' + str(changed or live.get('release') != candidate['release']).lower())


def alert():
    summary_path = Path('update-summary.json')
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}
    failed = os.environ['JOB_STATUS'] != 'success'
    late = summary.get('sourceLate', False)
    issues = json.loads(gh('issue', 'list', '--state', 'open', '--search', TITLE, '--json', 'number,title'))
    existing = next((issue for issue in issues if issue['title'] == TITLE), None)
    if failed or late:
        if not existing:
            body = f"{'Update did not finish verification. Inspect this run and the live health endpoint; prior durable releases are available for rollback.' if failed else 'CHIRPS Final is later than the normal release allowance.'}\n\nRun: {os.environ['RUN_URL']}\nData through: {summary.get('dataThrough', 'see run logs')}\nExpected through month: {summary.get('expectedThroughMonth', 'see run logs')}\n\nInspect the failed step or upstream listing, then rerun update monthly rainfall. No CDS request is involved."
            gh('issue', 'create', '--title', TITLE, '--body', body)
    elif existing:
        gh('issue', 'close', str(existing['number']))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['restore', 'snapshot', 'decide', 'alert'])
    parser.add_argument('--cache', type=Path)
    args = parser.parse_args()
    if args.command == 'restore':
        restore(args.cache)
    else:
        globals()[args.command]()


if __name__ == '__main__':
    main()
