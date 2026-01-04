# Jusu++ Minimal Language Server

This document explains the minimal LSP skeleton included in `tools/lsp_server.py`.

Requirements:
- Python 3.8+
- pygls (install with `pip install pygls`)

Run the server:

```bash
pip install pygls
python tools/lsp_server.py
```

This server currently:
- Responds to `initialize` by logging
- Handles `textDocument/didOpen` and publishes diagnostics when parser errors are found
- Provides **hover** (basic info for stdlib & builtin names)
- Provides **completions** (keywords, builtin functions, stdlib module names)

Next steps:
- Improve hover to show function signatures and docstrings derived from runtime
- Make completions context-aware (e.g., after dot enumerate attributes)
- Add more LSP features: signatureHelp, go-to-definition, document symbols, formatting
- Provide a packaged VS Code extension with tests

