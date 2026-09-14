import { cp, mkdir, rm } from "node:fs/promises";

const destination = new URL("../dist/", import.meta.url);
await rm(destination, { recursive: true, force: true });
await mkdir(destination, { recursive: true });
await cp(new URL("../site/", import.meta.url), destination, { recursive: true });
await cp(new URL("../data/", import.meta.url), new URL("./data/", destination), {
  recursive: true,
});
console.log("built static site in dist/");

