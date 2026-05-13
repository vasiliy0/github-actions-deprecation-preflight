from pathlib import Path
import importlib.util
import json
import sys
import tempfile
import unittest

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

    def test_markdown_renderer_includes_safety_note(self):
        text = scanner.render_markdown(scanner.scan(ROOT / "examples"))
        self.assertIn("GitHub Actions Deprecation Preflight", text)
        self.assertIn("Read-only local scan", text)
        self.assertIn("Summary by severity", text)

    def test_output_json_and_fail_on_severity(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "report.json"
            exit_code = scanner.main([str(ROOT / "examples"), "--format", "json", "--output", str(output), "--fail-on-severity", "high"])
            self.assertEqual(exit_code, 1)
            report = json.loads(output.read_text())
            self.assertEqual(report["summary_by_severity"]["high"], 3)

    def test_fail_on_severity_stays_zero_above_findings(self):
        exit_code = scanner.main([str(ROOT / "examples"), "--fail-on-severity", "high"])
        self.assertEqual(exit_code, 1)

if __name__ == "__main__":
    unittest.main()
