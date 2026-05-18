# Rule inventory

Generated from the local prototype rule model and intended for CI adoption review. Rules are static preflight signals: they point to workflow lines that deserve migration review; they do not claim that every workflow is broken.

## Implemented rules

| Rule | Severity | Detects | Why it matters | False-positive notes | Remediation | Example |
|---|---:|---|---|---|---|---|
| `upload-artifact-v3` | high | `actions/upload-artifact@v3` in workflows/docs | v3 is retired/deprecated; artifact behavior changed in newer majors. | A historical Markdown snippet may be intentionally archived. | Upgrade to `actions/upload-artifact@v4`; review overwrite/merge assumptions, retention, and missing-file behavior. | `examples/artifact-cache-risk/.github/workflows/workflow.yml` |
| `download-artifact-v3` | high | `actions/download-artifact@v3` in workflows/docs | v3 is retired/deprecated; artifact naming/path assumptions may change during migration. | Old docs may be reference-only. | Upgrade to `actions/download-artifact@v4`; verify names, paths, and multi-artifact behavior. | `examples/artifact-cache-risk/.github/workflows/workflow.yml` |
| `cache-v3` | medium | `actions/cache@v3` | Cache action majors are recurring migration hotspots and can hide release blockers. | A pinned old major may be temporarily required for legacy workflows. | Upgrade to `actions/cache@v4`; verify keys, restore behavior, and cache misses in a non-release branch. | `examples/artifact-cache-risk/.github/workflows/workflow.yml` |
| `checkout-v3` | medium | `actions/checkout@v3` | Older checkout majors can lag runtime/security maintenance. | Some repos pin old majors while validating token/submodule behavior. | Upgrade to `actions/checkout@v4`; verify submodules, LFS, token permissions, and fetch-depth. | `examples/ubuntu-runner-risk/.github/workflows/workflow.yml` |
| `setup-node-v3` | medium | `actions/setup-node@v3` | Older setup-node majors can lag runtime/cache changes. | Legacy Node projects may need staged validation. | Upgrade to `actions/setup-node@v4`; verify `node-version`, cache settings, and lockfile behavior. | `examples/ubuntu-runner-risk/.github/workflows/workflow.yml` |
| `local-action-node16` | high | local `action.yml` / `action.yaml` with `runs.using: node16` | Local JavaScript actions running on Node 16 are a runtime deprecation risk. | A vendored example action may not run in CI. | Move runtime to `node20`/`node24` as supported, rebuild dependencies, and test the action on a branch. | `examples/node-runtime-risk/.github/actions/build-check/action.yml` |
| `local-action-node20-review` | low | local `action.yml` / `action.yaml` with `runs.using: node20` | Tracks future runtime review windows before they become urgent. | Expected for current actions; usually informational only. | Keep a runtime upgrade note in the platform backlog; do not block PRs unless your policy requires it. | Create by changing the node-runtime example to `node20`. |

## CLI support

- Use `--list-rules` for a Markdown inventory.
- Use `--list-rules --format json` for machine-readable inventory.
- Use `--only-rule` / `--ignore-rule` for scoped CI rollout.
- Use `--min-severity` for high-risk-only reports.
- Use `--fail-on-severity high` only after the team has reviewed expected findings.

## Outreach-safe examples

The public-safe examples are intentionally synthetic and contain no private organization names, tokens, internal paths, or customer data:

- `examples/node-runtime-risk/` — local action runtime risk.
- `examples/ubuntu-runner-risk/` — older checkout/setup-node majors often reviewed during runner/runtime migrations.
- `examples/artifact-cache-risk/` — artifact/cache migration risks.
- `examples/sample-report.md` and `examples/sample-report.json` — generated scanner output.

## Safety posture

Rules are static review prompts. The scanner does not call GitHub APIs, fetch changelogs, mutate workflow files, or claim automatic migration safety.
