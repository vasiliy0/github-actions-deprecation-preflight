# GitHub Actions Deprecation Preflight v0.1.2

Agent/CI integration release.

## Added

- Versioned JSON report contract fields: `schema_version`, `tool`, `tool_version`, `status`, `summary`, and `metadata`.
- Stable finding fingerprints for reruns and agent workflows.
- GitHub Actions annotation output via `--format annotations`.
- JSON schema at `schemas/report.schema.json`.
- AI-agent integration guide at `docs/AGENT_INTEGRATION.md`.
- Automation-safe `--quiet` and `--no-color` flags.

## Compatibility

Existing Markdown/JSON reports, rule filters, `--list-rules`, and severity gates remain available.
