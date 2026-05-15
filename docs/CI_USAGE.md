# CI usage draft

Use this scanner as a read-only preflight before upgrading GitHub Actions workflow dependencies.

## Report-only step

```yaml
- name: GitHub Actions deprecation preflight
  run: |
    python -m pip install github-actions-deprecation-preflight
    gha-deprecation-preflight . --format markdown --output gha-deprecation-report.md
```

## High-risk gate after review

```yaml
- name: GitHub Actions deprecation preflight
  run: |
    gha-deprecation-preflight . \
      --format json \
      --output gha-deprecation-report.json \
      --min-severity high \
      --fail-on-severity high
```

## Scoped rollout

```bash
gha-deprecation-preflight . --only-rule upload-artifact-v3
gha-deprecation-preflight . --ignore-rule local-action-node20-review
```

Recommended flow: run report-only first, fix high-severity retired actions, then decide whether a high-severity gate is useful for the repo.
