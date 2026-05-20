# Suite integration: GitHub Actions Deprecation Preflight

Role in Engineering Risk Preflight suite: focused CI deprecation/runtime scanner.

## Standalone value

Use this tool when a maintainer wants a narrow, low-noise review of GitHub Actions versions and local action runtime migration risks.

## Relationship to repo-hygiene-ci-risk-preflight

- Repo Hygiene is broader: ownership files, release guardrails, CI observability, permissions, dependency hygiene.
- GitHub Actions Deprecation Preflight is deeper for Actions/runtime migration.
- Future suite reports can link to this tool's findings as the `ci-deprecation` signal.

## Alignment targets

- Keep CLI flags consistent with the suite: `--format`, `--output`, `--min-severity`, `--fail-on-severity`, `--only-rule`, `--ignore-rule`, `--list-rules`.
- Keep rule metadata fields consistent: `id`, `severity`, `why`, `fix`, and optional `confidence/category` in a future v0.1.2.
- Keep no-token/no-network default.

## Local next improvements

- Add more runtime/deprecation fixtures.
- Add stable finding fingerprints.
- Add GitHub annotation output if needed.
- Prepare v0.1.2 release notes locally; publish only with approval.
