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
SEVERITY_ORDER = {"low": 1, "medium": 2, "high": 3}

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

def filter_rules(rules: Iterable[Rule], only_rule: set[str] | None = None, ignore_rule: set[str] | None = None) -> list[Rule]:
    only_rule = only_rule or set()
    ignore_rule = ignore_rule or set()
    filtered = []
    known_ids = {rule.id for rule in rules}
    unknown_only = only_rule - known_ids
    unknown_ignore = ignore_rule - known_ids
    if unknown_only or unknown_ignore:
        unknown = ", ".join(sorted(unknown_only | unknown_ignore))
        raise ValueError(f"Unknown rule id(s): {unknown}")
    for rule in rules:
        if only_rule and rule.id not in only_rule:
            continue
        if rule.id in ignore_rule:
            continue
        filtered.append(rule)
    return filtered

def scan_file(path: Path, root: Path, rules: Iterable[Rule]) -> list[Finding]:
    text = path.read_text(encoding="utf-8", errors="replace")
    findings: list[Finding] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        for rule in rules:
            if re.search(rule.pattern, line, flags=re.I):
                findings.append(Finding(str(path.relative_to(root)), idx, rule.id, rule.severity, line.strip(), rule.why, rule.fix))
    return findings

def scan(root: Path, rules_path: Path = DEFAULT_RULES, only_rule: set[str] | None = None, ignore_rule: set[str] | None = None) -> dict:
    rules = filter_rules(load_rules(rules_path), only_rule=only_rule, ignore_rule=ignore_rule)
    files = discover(root)
    findings: list[Finding] = []
    for file in files:
        findings.extend(scan_file(file, root, rules))
    return {
        "scanned_files": len(files),
        "active_rule_count": len(rules),
        "finding_count": len(findings),
        "findings": [asdict(f) for f in findings],
        "summary_by_severity": severity_summary(findings),
        "summary_by_rule": rule_summary(findings),
        "notes": [
            "Read-only local scan; no GitHub API calls or uploads.",
            "Prototype rules are conservative and should be reviewed against official action changelogs before automated migrations.",
        ],
    }

def severity_summary(findings: list[Finding]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for finding in findings:
        summary[finding.severity] = summary.get(finding.severity, 0) + 1
    return summary

def rule_summary(findings: list[Finding]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for finding in findings:
        summary[finding.rule_id] = summary.get(finding.rule_id, 0) + 1
    return summary

def render_markdown(report: dict) -> str:
    lines = ["# GitHub Actions Deprecation Preflight", "", f"Scanned files: {report['scanned_files']}", f"Active rules: {report.get('active_rule_count', 'n/a')}", f"Findings: {report['finding_count']}", ""]
    if report.get("summary_by_severity"):
        lines.append("## Summary by severity")
        for severity, count in report["summary_by_severity"].items():
            lines.append(f"- **{severity}**: {count}")
        lines.append("")
    if report.get("summary_by_rule"):
        lines.append("## Summary by rule")
        for rule_id, count in report["summary_by_rule"].items():
            lines.append(f"- `{rule_id}`: {count}")
        lines.append("")
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
    parser.add_argument("--output", "-o", help="Write report to a file instead of stdout")
    parser.add_argument("--fail-on-severity", choices=["low", "medium", "high"], help="Exit 1 when findings at or above this severity are detected")
    parser.add_argument("--only-rule", action="append", default=[], help="Run only this rule id; repeat for multiple rules")
    parser.add_argument("--ignore-rule", action="append", default=[], help="Skip this rule id; repeat for multiple rules")
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    args = parser.parse_args(argv)
    try:
        report = scan(Path(args.path).resolve(), args.rules, only_rule=set(args.only_rule), ignore_rule=set(args.ignore_rule))
    except ValueError as exc:
        parser.error(str(exc))
    output = json.dumps(report, indent=2) if args.format == "json" else render_markdown(report)
    if args.output:
        Path(args.output).write_text(output + ("" if output.endswith("\n") else "\n"), encoding="utf-8")
    else:
        print(output, end="" if args.format == "markdown" else "\n")
    if args.fail_on_severity and should_fail(report, args.fail_on_severity):
        return 1
    return 0

def should_fail(report: dict, threshold: str) -> bool:
    minimum = SEVERITY_ORDER[threshold]
    return any(SEVERITY_ORDER.get(item["severity"], 0) >= minimum for item in report["findings"])

if __name__ == "__main__":
    raise SystemExit(main())
