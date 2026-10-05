"""Fetch public JSON using the runner's curl client and normal HTTP retries."""
import json
import subprocess


def fetch_json(url):
    result = subprocess.run(['curl', '--fail', '--silent', '--show-error', '--retry', '3', '--retry-delay', '2',
                             '--connect-timeout', '15', '--max-time', '45',
                             '--header', 'Cache-Control: no-cache', '--header', 'Accept: application/json', url],
                            check=True, capture_output=True, text=True)
    return json.loads(result.stdout)
