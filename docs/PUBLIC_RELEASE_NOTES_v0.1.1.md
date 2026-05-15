# GitHub Actions Deprecation Preflight v0.1.1 draft

Status: local draft, not published.

## Prepared locally

- CI usage guide with report-only and high-risk gate examples.
- Clearer scoped rollout commands for `--only-rule` and `--ignore-rule`.
- Release checklist for a future package push.
- Local wheel/install readiness notes for TestPyPI/PyPI preparation.

## Release checklist

- [x] Existing unit tests pass locally.
- [x] Package metadata exists locally for Python CLI packaging.
- [x] Local wheel build and clean virtualenv install verified.
- [ ] User approval for GitHub push.
- [ ] User approval for TestPyPI/PyPI publish, if desired.
