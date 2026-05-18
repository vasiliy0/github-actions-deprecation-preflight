# GitHub Actions Deprecation Preflight

Scanned files: 3
Active rules: 7
Findings: 6

## Summary by severity
- **high**: 3
- **medium**: 3

## Summary by rule
- `local-action-node16`: 1
- `checkout-v3`: 1
- `cache-v3`: 1
- `upload-artifact-v3`: 1
- `download-artifact-v3`: 1
- `setup-node-v3`: 1

## Findings
- **high** `local-action-node16` in `.github/actions/local-action/action.yml:3`
  - Signal: `using: node16`
  - Why: Local JavaScript actions running on Node 16 are a runtime deprecation risk.
  - Fix: Move the local action runtime to node20/node24 as supported, rebuild dependencies, and test on a branch.
- **medium** `checkout-v3` in `.github/workflows/ci.yml:7`
  - Signal: `- uses: actions/checkout@v3`
  - Why: Older checkout major versions can lag runtime/security maintenance.
  - Fix: Upgrade to actions/checkout@v4 and verify submodule/LFS/token behavior if used.
- **medium** `cache-v3` in `.github/workflows/ci.yml:8`
  - Signal: `- uses: actions/cache@v3`
  - Why: Older cache major versions are recurring deprecation/migration hotspots.
  - Fix: Upgrade to actions/cache@v4 and verify cache key/restore behavior in a non-release branch.
- **high** `upload-artifact-v3` in `.github/workflows/ci.yml:12`
  - Signal: `- uses: actions/upload-artifact@v3`
  - Why: upload-artifact v3 is retired/deprecated; workflows should move to the current major.
  - Fix: Upgrade to actions/upload-artifact@v4 and review changed artifact behavior, overwrite/merge assumptions, and retention settings.
- **high** `download-artifact-v3` in `docs/snippet.md:2`
  - Signal: `- uses: actions/download-artifact@v3`
  - Why: download-artifact v3 is retired/deprecated; workflows should move to the current major.
  - Fix: Upgrade to actions/download-artifact@v4 and verify artifact naming/path assumptions.
- **medium** `setup-node-v3` in `docs/snippet.md:3`
  - Signal: `- uses: actions/setup-node@v3`
  - Why: Older setup-node major versions can lag runtime/security maintenance.
  - Fix: Upgrade to actions/setup-node@v4 and verify node-version/cache behavior.

## Notes
- Read-only local scan; no GitHub API calls or uploads.
- Prototype rules are conservative and should be reviewed against official action changelogs before automated migrations.
