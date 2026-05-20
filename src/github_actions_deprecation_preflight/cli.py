#!/usr/bin/env python3
"""Local read-only GitHub Actions deprecation preflight prototype."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from . import __version__

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
    fingerprint: str

def load_rules(path: Path = DEFAULT_RULES) -> list[Rule]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [Rule(**item) for item in data["rules"]]

def is_generated_report(path: Path) -> bool:
    return path.name in {"sample-report.md", "sample-report.json", "sample-annotations.txt", "report.md", "report.json", "annotations.txt"}

def discover(root: Path) -> list[Path]:
    candidates: list[Path] = []
    workflow_dir = root / ".github" / "workflows"
    if workflow_dir.exists():
        candidates.extend(p for p in workflow_dir.rglob("*") if p.is_file() and p.suffix.lower() in {".yml", ".yaml"} and not is_generated_report(p))
    actions_dir = root / ".github" / "actions"
    if actions_dir.exists():
        candidates.extend(p for p in actions_dir.rglob("action.*ml") if p.is_file() and not is_generated_report(p))
    candidates.extend(p for p in root.rglob("*.md") if p.is_file() and not is_generated_report(p))
    candidates.extend(p for p in root.rglob("*.mdx") if p.is_file() and not is_generated_report(p))
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
                rel_path = str(path.relative_to(root))
                signal = line.strip()
                fingerprint = make_fingerprint(rule.id, rel_path, idx, signal)
                findings.append(Finding(rel_path, idx, rule.id, rule.severity, signal, rule.why, rule.fix, fingerprint))
    return findings

def make_fingerprint(rule_id: str, file: str, line: int, signal: str) -> str:
    data = "|".join([rule_id, file, str(line), signal.strip()[:240]])
    return hashlib.sha256(data.encode("utf-8")).hexdigest()[:16]

def scan(root: Path, rules_path: Path = DEFAULT_RULES, only_rule: set[str] | None = None, ignore_rule: set[str] | None = None) -> dict:
    rules = filter_rules(load_rules(rules_path), only_rule=only_rule, ignore_rule=ignore_rule)
    files = discover(root)
    findings: list[Finding] = []
    for file in files:
        findings.extend(scan_file(file, root, rules))
    return {
        "schema_version": "1.0",
        "tool": "github-actions-deprecation-preflight",
        "tool_version": __version__,
        "version": __version__,
        "status": "warning" if findings else "ok",
        "scanned_files": len(files),
        "active_rule_count": len(rules),
        "finding_count": len(findings),
        "findings": [asdict(f) for f in findings],
        "summary_by_severity": severity_summary(findings),
        "summary_by_rule": rule_summary(findings),
        "summary": {
            "scanned_files": len(files),
            "active_rule_count": len(rules),
            "finding_count": len(findings),
            "summary_by_severity": severity_summary(findings),
            "summary_by_rule": rule_summary(findings),
        },
        "metadata": {
            "privacy": "local-only; no GitHub API, token, network call, source upload, or telemetry",
        },
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

def filter_findings_by_severity(findings: list[Finding], minimum_severity: str | None = None) -> list[Finding]:
    if not minimum_severity:
        return findings
    minimum = SEVERITY_ORDER[minimum_severity]
    return [finding for finding in findings if SEVERITY_ORDER.get(finding.severity, 0) >= minimum]

def apply_report_filters(report: dict, minimum_severity: str | None = None) -> dict:
    if not minimum_severity:
        return report
    findings = [Finding(**item) for item in report["findings"]]
    filtered = filter_findings_by_severity(findings, minimum_severity)
    notes = list(report["notes"])
    notes.append(f"Filtered findings below {minimum_severity} severity.")
    return {
        **report,
        "finding_count": len(filtered),
        "findings": [asdict(f) for f in filtered],
        "summary_by_severity": severity_summary(filtered),
        "summary_by_rule": rule_summary(filtered),
        "notes": notes,
    }

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

def render_annotations(report: dict) -> str:
    level = {"high": "error", "medium": "warning", "low": "notice"}
    lines: list[str] = []
    for item in report["findings"]:
        file = item["file"]
        line = max(int(item["line"]), 1)
        title = f"{item['rule_id']} ({item['severity']})"
        message = f"{item['why']} Fix: {item['fix']} Fingerprint: {item.get('fingerprint', '')}"
        message = message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        lines.append(f"::{level.get(item['severity'], 'notice')} file={file},line={line},title={title}::{message}")
    return "\n".join(lines) + ("\n" if lines else "")

def render_rule_inventory(rules: list[Rule], output_format: str = "markdown") -> str:
    if output_format == "json":
        return json.dumps({"rules": [asdict(rule) for rule in rules]}, indent=2) + "\n"
    lines = ["# GitHub Actions Deprecation Preflight rule inventory", ""]
    for rule in rules:
        lines.append(f"## `{rule.id}`")
        lines.append("")
        lines.append(f"- Severity: **{rule.severity}**")
        lines.append(f"- Pattern: `{rule.pattern}`")
        lines.append(f"- Why: {rule.why}")
        lines.append(f"- Fix: {rule.fix}")
        lines.append("")
    return "\n".join(lines)

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan GitHub Actions files for deprecation risks.")
    parser.add_argument("path", nargs="?", default=".", help="Repository root to scan")
    parser.add_argument("--format", choices=["markdown", "json", "annotations"], default="markdown")
    parser.add_argument("--output", "-o", help="Write report to a file instead of stdout")
    parser.add_argument("--fail-on-severity", choices=["low", "medium", "high"], help="Exit 1 when findings at or above this severity are detected")
    parser.add_argument("--min-severity", choices=["low", "medium", "high"], help="Only include findings at or above this severity in the report")
    parser.add_argument("--only-rule", action="append", default=[], help="Run only this rule id; repeat for multiple rules")
    parser.add_argument("--ignore-rule", action="append", default=[], help="Skip this rule id; repeat for multiple rules")
    parser.add_argument("--list-rules", action="store_true", help="Print the active rule inventory and exit")
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    parser.add_argument("--quiet", action="store_true", help="Automation-friendly no-op: suppresses future non-report diagnostics; reports still write normally.")
    parser.add_argument("--no-color", action="store_true", help="Automation-friendly no-op: output is plain text by default and never requires color.")
    args = parser.parse_args(argv)
    try:
        active_rules = filter_rules(load_rules(args.rules), only_rule=set(args.only_rule), ignore_rule=set(args.ignore_rule))
        if args.list_rules:
            print(render_rule_inventory(active_rules, args.format), end="")
            return 0
        report = scan(Path(args.path).resolve(), args.rules, only_rule=set(args.only_rule), ignore_rule=set(args.ignore_rule))
    except ValueError as exc:
        parser.error(str(exc))
    report = apply_report_filters(report, args.min_severity)
    if args.format == "json":
        output = json.dumps(report, indent=2)
    elif args.format == "annotations":
        output = render_annotations(report)
    else:
        output = render_markdown(report)
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
