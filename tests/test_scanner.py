from pathlib import Path
import importlib.util
import sys
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

if __name__ == "__main__":
    unittest.main()
