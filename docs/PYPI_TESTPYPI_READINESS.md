# PyPI/TestPyPI readiness notes

Status: local readiness only. No TestPyPI or PyPI upload has been performed.

## Current local package

- Package: `github-actions-deprecation-preflight`
- Local version: `0.1.1`
- CLI entry points:
  - `github-actions-deprecation-preflight`
  - `gha-deprecation-preflight`
- Runtime model: local read-only scanner; no GitHub API, token, account, network call, or file mutation.

## Local checks completed

- Unit tests: passed (`8` tests).
- Python syntax compile: passed for scanner, package modules, and tests.
- Wheel build via `pip wheel .`: passed.
- Clean virtualenv install from local wheel: passed.
- Installed package module execution: passed:

```bash
python -m github_actions_deprecation_preflight.cli examples --format json --output install-check-report.json
```

Result: scanner found the expected sample findings: `3` high and `3` medium findings across artifact/action/runtime rules.

## Notes

- `python3 -m build` is not available in the current environment because the `build` module is not installed; `pip wheel .` was used as the local packaging readiness check instead.
- Public package API read-only check found no existing `github-actions-deprecation-preflight` project on PyPI or TestPyPI.
- Uploading to TestPyPI/PyPI, creating a GitHub release/tag, or pushing these local changes requires explicit approval.

## Pre-publish checklist

- [x] Version bumped locally to `0.1.1`.
- [x] Release notes draft exists.
- [x] CI usage docs exist.
- [x] Unit tests pass locally.
- [x] Local wheel builds and installs.
- [ ] Approval for GitHub push.
- [ ] Approval for TestPyPI dry run.
- [ ] Approval for production PyPI publish.
- [ ] Post-publish install verification in clean environment.

## 2026-05-14 TestPyPI publish attempt status

- User approval scope: TestPyPI only for `github-actions-deprecation-preflight`; no production PyPI, GitHub push/release, or outreach.
- Metadata inspected: package `github-actions-deprecation-preflight`, version `0.1.1`.
- Secret scan over package source/docs/config found no token-like values.
- Tests passed: `8` unit tests.
- Syntax compile passed.
- `python -m build` produced wheel and sdist.
- `twine check dist/*` passed.
- Dist contents inspected: expected package files, README, LICENSE, pyproject, rules JSON, and tests in sdist.
- TestPyPI read-only check: package not found yet.
- Upload not performed because no TestPyPI credentials/token were available via environment or `.pypirc`; no credential prompt/token handling was attempted.

To complete TestPyPI publishing, provide a TestPyPI API token via an approved secret mechanism/environment variable, or approve a separate GitHub Trusted Publishing workflow path.

## 2026-05-15 TestPyPI upload attempt

- User approval scope: TestPyPI upload only for `github-actions-deprecation-preflight` v0.1.1; no production PyPI, GitHub push/release, or outreach.
- Checks re-run: unit tests passed (`8`), syntax compile passed.
- Packaging tool note: system `twine` was too old for Metadata-Version 2.4, so a temporary local venv with `build` and `twine 6.2.0` was used for validation.
- Build passed: wheel and sdist built with `/workspace/.tmp-twine-upload/bin/python -m build`.
- Metadata check passed: `/workspace/.tmp-twine-upload/bin/twine check dist/*`.
- Upload command attempted: `/workspace/.tmp-twine-upload/bin/twine upload --repository-url https://test.pypi.org/legacy/ --non-interactive dist/*`.
- Result: upload blocked before transfer because no TestPyPI API token/credential was available: `NonInteractive: Credential not found for API token`. Trusted Publishing is not supported in this environment.
- TestPyPI status after attempt: package still returns 404.

Needed next: provide a TestPyPI API token via approved secret mechanism/environment variable, or approve a GitHub Trusted Publishing workflow path from a supported GitHub Actions environment.

## 2026-05-15 TestPyPI Trusted Publishing success

- Scoped approval: GitHub push of v0.1.1 package/workflow changes and workflow_dispatch `target=testpypi` only. No production PyPI, GitHub release/tag, outreach, marketplace, or payment action.
- GitHub commit pushed: `33f9a88` (`Prepare v0.1.1 TestPyPI publishing`).
- Workflow: `publish.yml`, run `25922435274`, target `testpypi`.
- Result: `publish-testpypi` succeeded; `publish-pypi` was skipped by workflow condition.
- TestPyPI: https://test.pypi.org/project/github-actions-deprecation-preflight/0.1.1/
- Uploaded files observed via TestPyPI JSON:
  - `github_actions_deprecation_preflight-0.1.1-py3-none-any.whl`
  - `github_actions_deprecation_preflight-0.1.1.tar.gz`
