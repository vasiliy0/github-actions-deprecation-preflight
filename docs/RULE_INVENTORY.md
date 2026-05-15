# Rule inventory

Generated from the local prototype rule model and intended for CI adoption review.

## Implemented rules

| Rule | Severity | Intent |
|---|---:|---|
| `upload-artifact-v3` | high | Flag retired/deprecated upload-artifact v3 usage. |
| `download-artifact-v3` | high | Flag retired/deprecated download-artifact v3 usage. |
| `cache-v3` | medium | Review older cache major versions before recurring migration windows. |
| `checkout-v3` | medium | Review older checkout major versions for maintenance/runtime lag. |
| `setup-node-v3` | medium | Review older setup-node major versions before runtime/cache changes. |
| `local-action-node16` | high | Flag local JavaScript actions still using the Node 16 runtime. |
| `local-action-node20-review` | low | Track local Node 20 actions for future runtime schedule review. |

## CLI support

- Use `--list-rules` for a Markdown inventory.
- Use `--list-rules --format json` for machine-readable inventory.
- Use `--only-rule` / `--ignore-rule` for scoped CI rollout.
- Use `--min-severity` for high-risk-only reports.

## Safety posture

Rules are static review prompts. The scanner does not call GitHub APIs, fetch changelogs, mutate workflow files, or claim automatic migration safety.
