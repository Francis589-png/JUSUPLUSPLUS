# Unreal Engine Integration (Jusu++)

This guide explains recommended integration patterns to use Jusu++ with Unreal Engine.

Integration options
-------------------
1. External Bridge (recommended for prototyping)
   - Run `projects/unreal_plugin/jusu_unreal_bridge.py` as a separate process.
   - From Unreal (C++ plugin, Blueprint, or Python plugin), connect via TCP and send JSON requests that ask the bridge to `run_script` or `run_script_path`.
   - Protect the bridge with network restrictions and run it in a sandbox in production.

2. HTTP gateway
   - Wrap the bridge with a thin HTTP server if easier for Unreal-side integration.

3. Native plugin (advanced)
   - Create a C++ plugin that launches/communicates with the bridge, or embed a compiled runtime.
   - Requires C++ knowledge and packaging steps for packaging into `.uplugin`/`.uproject`.

Example flow (using TCP bridge)
-------------------------------
- Unreal actor needs AI decision: serialize actor state -> send JSON to bridge -> receive JSON decision -> apply in Unreal.
- Keep messages small and stateless for robustness.

Example game script templates
-----------------------------
- `projects/unreal_plugin/examples/platformer.jusu` — enemy patrol + jump behavior
- `.../fps_enemy_ai.jusu` — FPS decision logic
- `.../rts_unit_behavior.jusu` — RTS unit behavior
- `.../rpg_npc_dialog.jusu` — RPG dialog gating

Security & deployment
---------------------
- **Authentication:** the bridge supports optional token-based auth (`--auth-token`). Include `auth_token` in each request (or set it in your editor tooling) to protect the socket.
- **TLS:** optional TLS support is available via `--tls-cert` and `--tls-key` to wrap the listener socket.
- **Sandboxing:** the bridge can run scripts via the built-in sandbox (`--use-sandbox` and `--mem-limit`), which enforces timeouts and (on Unix) memory limits using `runtime/sandbox.py`.
  - **Optional seccomp (Linux):** if `python-seccomp` (the `seccomp` module) is available on the node where the sandbox child runs, the child will attempt to install a restrictive seccomp filter to limit allowed syscalls. This is opt-in and best-effort (the sandbox continues to run if seccomp cannot be enabled). Install `python-seccomp` on the host to enable seccomp.
  - **Windows Job Objects:** on Windows, if `pywin32` is present, the sandbox child will attempt to assign itself to a Job object (basic stub). For stricter job-object limits, integrate additional job configuration in your host environment.
- For production, run the bridge under OS-level process isolation (cgroups/containers), network restrictions, and follow your platform's hardened deployment patterns.

C++ plugin skeleton (starter)
-----------------------------
A small skeleton is included at `projects/unreal_plugin/unreal_example_plugin/` with several sample stubs:

- `Source/JusuUnrealPlugin/Public/JusuBridge.h` — header with `CallBridge` and placeholders
- `Source/JusuUnrealPlugin/Private/JusuBridge.cpp` — simple placeholder that logs a request
- `Source/JusuUnrealPlugin/Private/JusuBridge_FSocket.cpp` — example showing how to use UE `FSocket` to connect to the bridge and exchange JSON lines (blocking, synchronous; appropriate for editor tooling or simple calls)
- `Source/JusuUnrealPlugin/Private/JusuBridge_http.cpp` — example showing an HTTP call using `FHttpModule`.

Use these files as starting points — copy into your Unreal plugin project and adapt for your engine version and threading model. Ensure proper non-blocking or async use in gameplay code (the examples are simplified for clarity).

Blueprint/HTTP usage (Quick example)
-----------------------------------
You can use Unreal's HTTP module or Blueprints to call the HTTP gateway (`http_gateway.py`) or to directly POST to a wrapped bridge endpoint.

C++ (http) example using `FHttpModule`:

```
FString Url = "http://127.0.0.1:8777/run";
TSharedRef<IHttpRequest> Request = FHttpModule::Get().CreateRequest();
Request->SetURL(Url);
Request->SetVerb("POST");
Request->SetHeader("Content-Type", "application/json");
Request->SetContentAsString(RequestJsonString);
Request->OnProcessRequestComplete().BindLambda([](FHttpRequestPtr Req, FHttpResponsePtr Resp, bool bOk){
    if (bOk && Resp.IsValid()) {
        FString Body = Resp->GetContentAsString();
        // parse JSON and apply decisions to actor
    }
});
Request->ProcessRequest();
```

Blueprint (official nodes / pseudo):
- Use the `HTTP Request` node or a marketplace HTTP plugin.
- Configure a POST to `http://127.0.0.1:8777/run` with JSON body `{ "cmd": "run_script_path", "script_path": "<path>" }`.
- Decode the response and use `Break JSON` nodes to apply actor behavior.

Example Blueprint flow (steps):
1. Actor event -> Gather state -> Build JSON string
2. POST JSON to gateway `/run`
3. On response, parse JSON and apply operations (move/jump/attack) using Blueprint nodes

Security: Add `auth_token` to the JSON body if your gateway/bridge was started with `--auth-token`.

Next steps
----------
- Implement actual TCP/HTTP calls in `JusuBridge::CallBridge` for your engine code. A sample FSocket implementation (`JusuBridge_FSocket.cpp`) and an HTTP call example (`JusuBridge_http.cpp`) are included for reference.
- For Blueprint users: use the `HTTP Request` node to POST JSON to the gateway (`http://127.0.0.1:8777/run`) and decode responses to apply decisions.
- To experiment end-to-end: see `projects/unreal_plugin/unreal_sample_project/` for a small scaffold and `projects/unreal_plugin/examples/` for example AI scripts.

Sample project quickstart
-------------------------
1. Build the plugin zip: `python projects/unreal_plugin/tools/package_unreal_plugin.py`
2. Install into your Unreal project: `python projects/unreal_plugin/unreal_sample_project/scripts/install_plugin_into_unreal.py /path/to/YourUnrealProject`
3. Start the HTTP gateway: `python projects/unreal_plugin/http_gateway.py --port 8777` and enable `--use-sandbox` when running untrusted scripts.
4. In Blueprint, POST to `/run` and parse JSON responses to apply AI decisions.
- For production, prefer embedding or more robust IPC; the bridge is intended for prototyping and editor tools.

Notes
-----
This is a prototype integration pattern intended for demonstrations and tooling. For AAA shipping titles, teams usually prefer tighter runtime integrations (native modules, ahead-of-time compiled systems, or dedicated scripting runtimes integrated at engine build-time). This repo provides the prototyping bridge and patterns so you can evaluate workflows and iterate quickly.
