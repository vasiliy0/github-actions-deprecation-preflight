# GitHub Actions Deprecation Preflight

Read-only scanner for GitHub Actions workflow files, local JavaScript action metadata, and Markdown workflow snippets. It is meant to catch CI migration risks before they become broken builds or surprise release blockers.

Use it when a repository is preparing for GitHub Actions action-major upgrades, Node runtime changes, artifact/cache migrations, or runner-image cleanup.

## What this catches

Current v1 rules flag or review:

- retired/deprecated artifact actions: `actions/upload-artifact@v3`, `actions/download-artifact@v3`;
- older action majors that often need migration review: `actions/cache@v3`, `actions/checkout@v3`, `actions/setup-node@v3`;
- local JavaScript actions using old runtimes such as `runs.using: node16`;
- local JavaScript actions using `node20` as a low-severity future runtime review signal;
- workflow snippets inside Markdown docs, not only `.github/workflows/*.yml`.

It is intentionally narrow: this is a preflight checklist/scanner, not an automatic migration tool.

## 60-second quick start

```bash
python3 -m pip install github-actions-deprecation-preflight
gha-deprecation-preflight . --format markdown --output gha-deprecation-report.md
gha-deprecation-preflight . --format json --output gha-deprecation-report.json
gha-deprecation-preflight . --fail-on-severity high
```

Short alias:

```bash
gha-deprecation-preflight path/to/repo --min-severity high
```

PyPI: https://pypi.org/project/github-actions-deprecation-preflight/

## Example: failing workflow → finding → fix

Risky workflow snippet:

```yaml
jobs:
  build:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v3
      - uses: actions/cache@v3
        with:
          path: ~/.npm
          key: npm-${{ runner.os }}-${{ hashFiles('package-lock.json') }}
      - run: npm ci && npm test
      - uses: actions/upload-artifact@v3
        with:
          name: test-output
          path: test-results/
```

Scanner finding excerpt:

```text
- high `upload-artifact-v3`
  - Signal: `- uses: actions/upload-artifact@v3`
  - Why: upload-artifact v3 is retired/deprecated; workflows should move to the current major.
  - Fix: Upgrade to actions/upload-artifact@v4 and review changed artifact behavior, overwrite/merge assumptions, and retention settings.
```

Safer migration direction:

```yaml
      - uses: actions/cache@v4
        with:
          path: ~/.npm
          key: npm-${{ runner.os }}-${{ hashFiles('package-lock.json') }}
      - uses: actions/upload-artifact@v4
        with:
          name: test-output
          path: test-results/
          if-no-files-found: warn
```

Review current example fixtures and generated reports:

- [`examples/node-runtime-risk/`](examples/node-runtime-risk/)
- [`examples/ubuntu-runner-risk/`](examples/ubuntu-runner-risk/)
- [`examples/artifact-cache-risk/`](examples/artifact-cache-risk/)
- [`examples/sample-report.md`](examples/sample-report.md)
- [`examples/sample-report.json`](examples/sample-report.json)

## CI usage

See [`docs/CI_USAGE.md`](docs/CI_USAGE.md) for report-only, high-risk gate, and scoped rollout examples.

Minimal report-only GitHub Actions step:

```yaml
- name: GitHub Actions deprecation preflight
  run: |
    python -m pip install github-actions-deprecation-preflight
    gha-deprecation-preflight . --format markdown --output gha-deprecation-report.md
```

## Try from a clone

```bash
python3 scanner.py examples
python3 scanner.py examples --format json
python3 scanner.py examples --output report.md
python3 scanner.py examples --fail-on-severity high
python3 scanner.py examples --min-severity high
python3 scanner.py examples --only-rule upload-artifact-v3
python3 scanner.py --list-rules
python3 scanner.py --list-rules --format json
python3 scanner.py examples --ignore-rule local-action-node20-review
```

Example output:

```text
# GitHub Actions Deprecation Preflight

Scanned files: 6
Active rules: 7
Findings: 13
```

## Intended workflow

1. Run the scanner at a repository root.
2. Review high-severity findings first, especially retired artifact actions and old local JavaScript runtimes.
3. Use `--min-severity high` for a high-risk-only report, `--only-rule` while validating one migration family, or `--ignore-rule` for a documented false-positive/noise window.
4. Upgrade action majors on a branch.
5. Verify workflow behavior before merging.

## Safe by default

- Read-only local scan.
- No GitHub API calls.
- No GitHub token required.
- No workflow upload or telemetry.
- No automatic migrations or commits.
- CI failure is opt-in via `--fail-on-severity`.
- Rule filtering is explicit and local; unknown rule ids fail fast instead of silently changing coverage.
- `--list-rules` can be used to review active rule coverage before adding the scanner to CI.

## Related Engineering Risk Preflight tools

- [Repository Hygiene / CI Risk Preflight](https://github.com/vasiliy0/repo-hygiene-ci-risk-preflight) — broader repo/package/release-readiness checks.
- [Zod OpenAPI Contract Lint Kit](https://github.com/vasiliy0/zod-openapi-contract-lint-kit) — API contract drift checks for Zod/OpenAPI projects.
- [Playwright Flake Triage Toolkit](https://github.com/vasiliy0/playwright-flake-triage) — local triage for flaky Playwright reports and CI logs.

## Roadmap

- Expand the rule inventory as GitHub Actions deprecations change.
- Add more fixtures for common workflow patterns.
- Expand CI adoption examples and release notes.
- Keep the default mode deterministic, local, and read-only.
