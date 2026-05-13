# GitHub Actions Deprecation Preflight

Local read-only prototype that scans GitHub Actions workflow files, local JavaScript action metadata, and Markdown snippets for known deprecation/runtime migration risks.

## Current v1 scope

- `actions/upload-artifact@v3` and `actions/download-artifact@v3`
- `actions/cache@v3`, `actions/checkout@v3`, `actions/setup-node@v3` review signals
- local `action.yml` / `action.yaml` `runs.using: node16` runtime risk
- optional low-severity review signal for `runs.using: node20`

No GitHub API, tokens, accounts, or network calls are used.

## Try locally

```bash
python3 scanner.py examples
python3 scanner.py examples --format json
python3 scanner.py examples --output report.md
python3 scanner.py examples --fail-on-severity high
python3 scanner.py examples --only-rule upload-artifact-v3
python3 scanner.py examples --ignore-rule local-action-node20-review
```

Example output:

```text
# GitHub Actions Deprecation Preflight

Scanned files: 3
Active rules: 7
Findings: 6
```

## Intended workflow

1. Run the scanner at a repository root.
2. Review high-severity findings first, especially retired artifact actions and old local JavaScript runtimes.
3. Use `--only-rule` while validating one migration family, or `--ignore-rule` for a documented false-positive/noise window.
4. Upgrade action majors on a branch.
5. Verify workflow behavior before merging.

## Safety notes

- The scanner is read-only.
- It does not upload workflow contents.
- It does not need a GitHub token.
- It does not make automatic migrations.
- CI failure is opt-in via `--fail-on-severity`.
- Rule filtering is explicit and local; unknown rule ids fail fast instead of silently changing coverage.

## Roadmap

- Expand the rule inventory as GitHub Actions deprecations change.
- Add more fixtures for common workflow patterns.
- Add machine-readable rule inventory docs for CI adoption.
- Keep the default mode deterministic, local, and read-only.
