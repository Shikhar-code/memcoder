# MemCoder Studio

The Studio is a small Tauri desktop shell over MemCoder's localhost service.
It deliberately has no frontend framework or charting dependency.

It requires Python 3.10+, MemCoder installed in the environment used by the
shell, and Bun. Windows installer builds additionally require the normal Tauri
Rust/MSVC and WebView2 prerequisites.

From this directory, after the Windows Tauri prerequisites are installed:

```powershell
bun install
bun run dev
```

The first useful walkthrough is: open **Evidence** or **Dreaming**, choose
**Load Guided Demo**, then open Dreaming and press **Find New Connections**.
The demo is isolated under `studio-demo`, creates QA-approved example memories,
and does not modify real project memories.

To build the Windows installer (`.exe`):

```powershell
bun run build:exe
```

The installer is written to `src-tauri/target/release/bundle/nsis/`. The
unbundled application binary is written to `src-tauri/target/release/`.

The shell starts `memcoder service serve` automatically when the `memcoder`
command is available. To point it at a specific Python environment, set
`$env:MEMCODER_PYTHON` to that interpreter before launching.

The service remains the source of truth; the desktop UI does not duplicate the
memory engine or write SQLite/Chroma files directly.
