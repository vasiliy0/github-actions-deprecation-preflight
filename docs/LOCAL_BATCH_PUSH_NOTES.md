# Local batch push notes

Prepared locally while external action limits are paused.

## CLI rollout improvements

- `--min-severity` for high-risk-only report output.
- `--list-rules` in Markdown or JSON.
- Existing `--only-rule` / `--ignore-rule` can be combined with rule inventory output.

## Checks to rerun before push

```bash
python3 tests/test_scanner.py
python3 -m py_compile scanner.py tests/test_scanner.py
python3 scanner.py examples --format json --output /tmp/gha-report.json --min-severity high
python3 scanner.py --list-rules --format json
```

## Publication status

Code/docs only. No release, package publishing, marketplace listing, article, or outreach is included in this local batch.
