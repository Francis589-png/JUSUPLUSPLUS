Automation Agent — plugin-based automation runner

This demo shows a minimal automation agent that discovers plugins in `projects/automation_agent/plugins/`, loads them, and executes actions.

Plugin interface:
- A plugin is any Python module with a top-level `name` (str) and `run(context: dict) -> dict` function.

Quick start:
- Add a plugin to `projects/automation_agent/plugins/`.
- Run: `python projects/automation_agent/run_agent.py` (calls all discovered plugins).

This project includes unit tests and a CI workflow that runs on PRs.
