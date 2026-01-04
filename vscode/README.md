# Jusu++ VS Code Client (Minimal)

This is a minimal VS Code extension skeleton to run the Jusu++ LSP server.

How to use (development):
1. Open this workspace in VS Code and run `npm install` inside the `vscode` folder.
2. Press `F5` to launch an Extension Development Host which will start the server via the extension.
3. Open a `.jusu` file to see diagnostics, hover, and completions.

Notes:
- The client launches the Python server via `python tools/lsp_server.py`. Ensure the workspace's Python environment has `pygls` installed.
- This is intentionally minimal; a proper extension would include packaging, icons, and activation improvements.