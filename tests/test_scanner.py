from pathlib import Path
import importlib.util
import json
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("scanner", ROOT / "scanner.py")
scanner = importlib.util.module_from_spec(spec)
sys.modules["scanner"] = scanner
spec.loader.exec_module(scanner)

class TestScanner(unittest.TestCase):
    def test_example_finds_deprecated_actions_and_local_runtime(self):
        report = scanner.scan(ROOT / "examples")
        ids = {finding["rule_id"] for finding in report["findings"]}
        self.assertIn("upload-artifact-v3", ids)
        self.assertIn("download-artifact-v3", ids)
        self.assertIn("cache-v3", ids)
        self.assertIn("checkout-v3", ids)
        self.assertIn("setup-node-v3", ids)
        self.assertIn("local-action-node16", ids)
        self.assertEqual(report["summary_by_rule"]["upload-artifact-v3"], 1)

    def test_markdown_renderer_includes_safety_note_and_rule_summary(self):
        text = scanner.render_markdown(scanner.scan(ROOT / "examples"))
        self.assertIn("GitHub Actions Deprecation Preflight", text)
        self.assertIn("Read-only local scan", text)
        self.assertIn("Summary by severity", text)
        self.assertIn("Summary by rule", text)
        self.assertIn("Active rules", text)

    def test_output_json_and_fail_on_severity(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "report.json"
            exit_code = scanner.main([str(ROOT / "examples"), "--format", "json", "--output", str(output), "--fail-on-severity", "high"])
            self.assertEqual(exit_code, 1)
            report = json.loads(output.read_text())
            self.assertEqual(report["summary_by_severity"]["high"], 3)

    def test_fail_on_severity_stays_zero_above_findings(self):
        exit_code = scanner.main([str(ROOT / "examples"), "--only-rule", "checkout-v3", "--fail-on-severity", "high"])
        self.assertEqual(exit_code, 0)

    def test_only_rule_and_ignore_rule_filter_active_rules(self):
        only_report = scanner.scan(ROOT / "examples", only_rule={"upload-artifact-v3"})
        self.assertEqual(only_report["active_rule_count"], 1)
        self.assertEqual([f["rule_id"] for f in only_report["findings"]], ["upload-artifact-v3"])

        ignored_report = scanner.scan(ROOT / "examples", ignore_rule={"upload-artifact-v3", "download-artifact-v3", "local-action-node16"})
        ids = {finding["rule_id"] for finding in ignored_report["findings"]}
        self.assertNotIn("upload-artifact-v3", ids)
        self.assertNotIn("download-artifact-v3", ids)
        self.assertNotIn("local-action-node16", ids)
        self.assertEqual(ignored_report["summary_by_severity"].get("high"), None)

    def test_unknown_rule_is_cli_error(self):
        with mock.patch("sys.stderr"):
            with self.assertRaises(SystemExit):
                scanner.main([str(ROOT / "examples"), "--only-rule", "missing-rule"])

if __name__ == "__main__":
    unittest.main()
