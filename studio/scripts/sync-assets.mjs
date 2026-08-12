import { cpSync, mkdirSync, rmSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const studio = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const dist = resolve(studio, "dist");

rmSync(dist, { recursive: true, force: true });
mkdirSync(dist, { recursive: true });
cpSync(resolve(studio, "index.html"), resolve(dist, "index.html"));
cpSync(resolve(studio, "src"), resolve(dist, "src"), { recursive: true });
