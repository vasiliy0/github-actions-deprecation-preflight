# GitHub Actions Deprecation Preflight v0.1.0 draft

Initial local prototype for read-only GitHub Actions deprecation scanning.

## Includes

- Workflow scanner for `.github/workflows/*.yml` and `*.yaml`.
- Local action metadata scanner for `.github/actions/**/action.yml` / `action.yaml`.
- Markdown/MDX snippet scanner for docs and migration guides.
- Rules for artifact v3, cache/checkout/setup-node v3 review, and local `node16` action runtime risk.
- Markdown and JSON output.

## Safety posture

- Local-only, read-only scanner.
- No GitHub API calls.
- No tokens or credentials required.
- No repository contents uploaded.

## Known limitations

- Rules are conservative and do not replace official GitHub Actions changelogs.
- The scanner flags migration review needs; it does not edit workflow files.
