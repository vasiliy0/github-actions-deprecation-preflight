# AI agent and CI integration

This CLI is safe for agent workflows that need a local preflight for GitHub Actions deprecation and runtime migration risks.

## When an agent should run it

Run `gha-deprecation-preflight` before upgrading workflows, reviewing CI warnings, or planning action-major/runtime migrations. It is a detector, not an automatic migration tool.

## Safe commands

```bash
gha-deprecation-preflight . --format json --output gha-deprecation-report.json --quiet --no-color
gha-deprecation-preflight . --format annotations
gha-deprecation-preflight . --min-severity high --fail-on-severity high
gha-deprecation-preflight --list-rules --format json
```

## Machine contract

- JSON schema: `schemas/report.schema.json`.
- `schema_version`: `1.0`.
- Findings include `file`, `line`, `rule_id`, `severity`, `signal`, `why`, `fix`, and `fingerprint`.
- GitHub Actions annotations are available with `--format annotations`.

## Exit codes

- `0`: scan completed; report-only mode or no configured gate was tripped.
- `1`: scan completed and `--fail-on-severity` matched.
- `2`: usage/config/rule-id error from the CLI parser.
- `3`: reserved for future runtime/tool errors.

## Agent loop

1. Run JSON mode on a checked-out repo.
2. Sort findings by severity and rule.
3. Propose workflow edits on a branch: upgrade action majors, review local JS runtimes, preserve artifact/cache behavior.
4. Ask before applying changes or pushing.
5. Rerun and compare fingerprints.

## Safety

The tool reads local workflow/docs/action metadata only. It uses no GitHub API, token, network calls, telemetry, or source upload.
