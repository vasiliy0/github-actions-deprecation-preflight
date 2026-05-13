#!/usr/bin/env python3
"""Local read-only GitHub Actions deprecation preflight prototype."""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

DEFAULT_RULES = Path(__file__).with_name("rules.json")

@dataclass(frozen=True)
class Rule:
    id: str
    severity: str
    pattern: str
    why: str
    fix: str

@dataclass(frozen=True)
class Finding:
    file: str
    line: int
    rule_id: str
    severity: str
    signal: str
    why: str
    fix: str

def load_rules(path: Path = DEFAULT_RULES) -> list[Rule]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [Rule(**item) for item in data["rules"]]

def discover(root: Path) -> list[Path]:
    candidates: list[Path] = []
    workflow_dir = root / ".github" / "workflows"
    if workflow_dir.exists():
        candidates.extend(p for p in workflow_dir.rglob("*") if p.is_file() and p.suffix.lower() in {".yml", ".yaml"})
    actions_dir = root / ".github" / "actions"
    if actions_dir.exists():
        candidates.extend(p for p in actions_dir.rglob("action.*ml") if p.is_file())
    candidates.extend(p for p in root.rglob("*.md") if p.is_file())
    candidates.extend(p for p in root.rglob("*.mdx") if p.is_file())
    return sorted(set(candidates))

def scan_file(path: Path, root: Path, rules: Iterable[Rule]) -> list[Finding]:
    text = path.read_text(encoding="utf-8", errors="replace")
    findings: list[Finding] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        for rule in rules:
            if re.search(rule.pattern, line, flags=re.I):
                findings.append(Finding(str(path.relative_to(root)), idx, rule.id, rule.severity, line.strip(), rule.why, rule.fix))
    return findings

def scan(root: Path, rules_path: Path = DEFAULT_RULES) -> dict:
    rules = load_rules(rules_path)
    files = discover(root)
    findings: list[Finding] = []
    for file in files:
        findings.extend(scan_file(file, root, rules))
    return {
        "scanned_files": len(files),
        "finding_count": len(findings),
        "findings": [asdict(f) for f in findings],
        "notes": [
            "Read-only local scan; no GitHub API calls or uploads.",
            "Prototype rules are conservative and should be reviewed against official action changelogs before automated migrations.",
        ],
    }

def render_markdown(report: dict) -> str:
    lines = ["# GitHub Actions Deprecation Preflight", "", f"Scanned files: {report['scanned_files']}", f"Findings: {report['finding_count']}", ""]
    if report["findings"]:
        lines.append("## Findings")
        for item in report["findings"]:
            lines.append(f"- **{item['severity']}** `{item['rule_id']}` in `{item['file']}:{item['line']}`")
            lines.append(f"  - Signal: `{item['signal']}`")
            lines.append(f"  - Why: {item['why']}")
            lines.append(f"  - Fix: {item['fix']}")
    else:
        lines.append("No known deprecation signals found by the current rule set.")
    lines.extend(["", "## Notes"])
    for note in report["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan GitHub Actions files for deprecation risks.")
    parser.add_argument("path", nargs="?", default=".", help="Repository root to scan")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    args = parser.parse_args(argv)
    report = scan(Path(args.path).resolve(), args.rules)
    print(json.dumps(report, indent=2) if args.format == "json" else render_markdown(report), end="" if args.format == "markdown" else "\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
