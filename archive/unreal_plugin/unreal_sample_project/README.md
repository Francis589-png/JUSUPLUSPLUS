Unreal Sample Project (scaffold)

This folder contains a minimal scaffold and guidance for an Unreal project that demonstrates calling the Jusu++ bridge.

Contents:
- `JusuDrivenGame.uproject` — minimal .uproject file (placeholder)
- `Content/Blueprints` — suggested location for Blueprint assets (not included; instructions provided)
- `README.md` — this file

Notes:
- This is a starter scaffold. To use it:
  1. Create a new Unreal project (e.g., C++ or Blueprint).
  2. Build the plugin zip: `python projects/unreal_plugin/tools/package_unreal_plugin.py`
  3. Install into your project (example): `python projects/unreal_plugin/unreal_sample_project/scripts/install_plugin_into_unreal.py /path/to/YourUnrealProject`
  4. Open the project in Unreal Editor and enable the `JusuUnrealPlugin` under Plugins.
  5. Start the HTTP gateway locally: `python projects/unreal_plugin/http_gateway.py` (or `http_gateway_flask.py`).
  6. Create a Blueprint Actor and add a node that POSTs JSON to `http://127.0.0.1:8777/run` with body `{ "cmd": "run_script_path", "script_path": "<path>" }`.

Blueprint quick recipe (no binary assets):
- Event BeginPlay -> Build JSON string -> HTTP POST (/run) -> On Response: Parse JSON and apply actions (Set Actor Velocity, Jump, Play Anim)
- If using auth, add `auth_token` to the JSON body.

Developer tips
- For production-quality integration prefer asynchronous HTTP calls (non-blocking) and run the bridge with `--use-sandbox --mem-limit 256`.
- The sample script `projects/unreal_plugin/examples/platformer.jusu` demonstrates a small AI decision script. Modify it and observe behavior via Blueprint handling.

Security: Use `auth_token` and TLS for networked use; the sample project is for local experimentation only.
