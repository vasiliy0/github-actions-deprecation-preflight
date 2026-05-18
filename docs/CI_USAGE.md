# CI usage

Use this scanner as a read-only preflight before upgrading GitHub Actions workflow dependencies. Start in report-only mode, review the output, then optionally turn on a high-severity gate.

## Report-only workflow

```yaml
name: GitHub Actions deprecation preflight
on:
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  preflight:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.x"
      - name: Install scanner
        run: python -m pip install github-actions-deprecation-preflight
      - name: Generate Markdown report
        run: |
          gha-deprecation-preflight . \
            --format markdown \
            --output gha-deprecation-report.md
      - name: Add report to step summary
        if: always()
        run: cat gha-deprecation-report.md >> "$GITHUB_STEP_SUMMARY"
      - name: Upload report artifact
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: gha-deprecation-report
          path: gha-deprecation-report.md
```

## High-risk gate after review

Use this only after the team has reviewed expected findings and fixed or documented existing high-severity risks.

```yaml
name: GitHub Actions deprecation gate
on:
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  preflight:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.x"
      - name: Install scanner
        run: python -m pip install github-actions-deprecation-preflight
      - name: Fail on high-severity deprecation risks
        run: |
          gha-deprecation-preflight . \
            --format json \
            --output gha-deprecation-report.json \
            --min-severity high \
            --fail-on-severity high
      - name: Upload JSON report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: gha-deprecation-report-json
          path: gha-deprecation-report.json
```

## Scoped rollout examples

Run one migration family first:

```bash
gha-deprecation-preflight . --only-rule upload-artifact-v3
```

Temporarily suppress a reviewed low-noise rule while keeping the rest active:

```bash
gha-deprecation-preflight . --ignore-rule local-action-node20-review
```

Review active rules in CI logs before enabling a gate:

```bash
gha-deprecation-preflight --list-rules
```

## Recommended adoption path

1. Run report-only on pull requests and `workflow_dispatch`.
2. Fix high-severity retired artifact/runtime findings first.
3. Add a short note in the PR or tracking issue for any intentional exception.
4. Enable `--fail-on-severity high` only after expected high-severity findings are gone.
5. Keep medium/low findings as review prompts, not automatic blockers, unless the team has agreed on the policy.

## Safety posture

The scanner reads local repository files only. It does not call GitHub APIs, does not need a token, does not upload workflow contents, and does not modify files.
