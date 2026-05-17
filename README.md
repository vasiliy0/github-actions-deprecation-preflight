# GitHub Actions Deprecation Preflight

Local read-only prototype that scans GitHub Actions workflow files, local JavaScript action metadata, and Markdown snippets for known deprecation/runtime migration risks.

## Current v1 scope

- `actions/upload-artifact@v3` and `actions/download-artifact@v3`
- `actions/cache@v3`, `actions/checkout@v3`, `actions/setup-node@v3` review signals
- local `action.yml` / `action.yaml` `runs.using: node16` runtime risk
- optional low-severity review signal for `runs.using: node20`

No GitHub API, tokens, accounts, or network calls are used.

## Install from PyPI

```bash
python3 -m pip install github-actions-deprecation-preflight
github-actions-deprecation-preflight path/to/repo --format markdown
github-actions-deprecation-preflight path/to/repo --format json
github-actions-deprecation-preflight path/to/repo --fail-on-severity high
github-actions-deprecation-preflight --list-rules
```

Short alias:

```bash
gha-deprecation-preflight path/to/repo --min-severity high
```

PyPI: https://pypi.org/project/github-actions-deprecation-preflight/

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

Scanned files: 3
Active rules: 7
Findings: 6
```

## CI usage

See [`docs/CI_USAGE.md`](docs/CI_USAGE.md) for report-only, high-risk gate, and scoped rollout examples.

## Intended workflow

1. Run the scanner at a repository root.
2. Review high-severity findings first, especially retired artifact actions and old local JavaScript runtimes.
3. Use `--min-severity high` for a high-risk-only report, `--only-rule` while validating one migration family, or `--ignore-rule` for a documented false-positive/noise window.
4. Upgrade action majors on a branch.
5. Verify workflow behavior before merging.

## Safety notes

- The scanner is read-only.
- It does not upload workflow contents.
- It does not need a GitHub token.
- It does not make automatic migrations.
- CI failure is opt-in via `--fail-on-severity`.
- Rule filtering is explicit and local; unknown rule ids fail fast instead of silently changing coverage.
- `--list-rules` can be used to review active rule coverage before adding the scanner to CI.

## Roadmap

- Expand the rule inventory as GitHub Actions deprecations change.
- Add more fixtures for common workflow patterns.
- Expand CI adoption examples and release notes.
- Keep the default mode deterministic, local, and read-only.
