# Automation Agent

This document describes the Automation Agent: a simple plugin-based runner used in course projects and demos.

Usage:
- Add Python files to `projects/automation_agent/plugins/` that expose `name` and `run(context)`.
- Run with `python projects/automation_agent/run_agent.py`.

Testing:
- Unit tests live in `projects/automation_agent/tests/` and are run by CI.

Extending:
- Plugins can perform IO, call external services, or implement scheduled tasks. Keep destructive operations out of default plugins; prefer explicit opt-in plugins.
