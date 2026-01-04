Jusu++ — Unreal Engine Integration Plugin (prototype)

Overview
--------
This project provides a minimal, safe integration pattern to use Jusu++ as a scripting or AI language for Unreal Engine projects. It includes:

- `jusu_unreal_bridge.py`: a small JSON-over-TCP bridge that runs Jusu++ scripts on request and returns JSON responses. Ideal for rapid prototyping or editor tooling.
- Example high-level Jusu++ scripts for different game types (Platformer, FPS, RTS, RPG) under `examples/`.
- `tools/init_unreal_plugin.py`: scaffolding helper to generate plugin artifacts and integration notes.
- Docs describing recommended integration approaches (C++ plugin + IPC, HTTP bridge, or Unreal's Python plugin).

Design notes
------------
We intentionally keep the bridge external to Unreal for safety and development agility. There are two recommended approaches:

1. Simple IPC bridge (recommended for prototyping): run `jusu_unreal_bridge.py` as a separate process and have Unreal call it over TCP/HTTP. This keeps Jusu++ code fully isolated.

2. Native plugin approach (advanced): create a C++ Unreal plugin that launches or communicates with the bridge or that embeds the Jusu++ runtime via an appropriate FFI layer (advanced, requires C++ and build integration).

Security
--------
- Bridge runs external code; always run the bridge in a sandboxed environment for untrusted scripts.
- **Authentication:** the bridge supports an optional token via `--auth-token` and the request must include `auth_token` to be accepted.
- **TLS:** optional TLS is available via `--tls-cert` and `--tls-key` to secure transport.
- Consider network restrictions and process isolation for production deploys.

Getting started
---------------
- Start the bridge: `python projects/unreal_plugin/jusu_unreal_bridge.py --port 8765`
- From Unreal, connect to the bridge via desired IPC (TCP or HTTP) and send a JSON request like:
  {"cmd": "run_script", "script_path": "path/to/script.jusu", "args": {"entity_id": 1}}

See `docs/projects/unreal_plugin.md` for detailed instructions.
