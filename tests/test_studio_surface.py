"""The lightweight desktop shell stays dependency-light and points at the local service."""

import json
from pathlib import Path


root = Path(__file__).resolve().parents[1] / "studio"
package = json.loads((root / "package.json").read_text(encoding="utf-8"))
config = json.loads((root / "src-tauri" / "tauri.conf.json").read_text(encoding="utf-8"))

assert package["scripts"]["dev"].endswith("tauri dev")
assert package["scripts"]["build:exe"].endswith("tauri build --bundles nsis")
assert package.get("dependencies", {}) == {}
assert list(package["devDependencies"]) == ["@tauri-apps/cli"]
assert config["build"]["frontendDist"] == "../dist"
assert (root / "index.html").exists()
assert (root / "src" / "app.js").exists()
assert (root / "src" / "styles.css").exists()
assert (root / "src-tauri" / "src" / "main.rs").exists()
assert (root / "scripts" / "sync-assets.mjs").exists()
app = (root / "src" / "app.js").read_text(encoding="utf-8")
assert "Find New Connections" in app
assert "Memory Scope" in app
assert "No new connections found" in app

print("PASS: lightweight Studio surface")
