import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "assets/projects/calculator_check.py"
REFERENCE = (ROOT / "tool/projects/calculator_reference.py").read_text()

def check(code, step):
    run = subprocess.run([sys.executable, str(CHECKER)],
        input=json.dumps({"code": code, "step": step, "nonce": "test-token"}),
        text=True, capture_output=True, timeout=5, check=True)
    report = json.loads(run.stdout)
    assert report["nonce"] == "test-token"
    return report["checks"]

class CalculatorChecks(unittest.TestCase):
    def test_reference_passes_every_stage(self):
        for stage, count in enumerate([5, 6, 9, 14]):
            checks = check(REFERENCE, stage)
            self.assertEqual(len(checks), count)
            self.assertTrue(all(c["passed"] for c in checks), checks)

    def test_constant_answer_does_not_pass(self):
        self.assertTrue(any(not c["passed"] for c in check("def calculate(a,b,operation): return 11", 0)))

    def test_missing_history_does_not_pass(self):
        bad = REFERENCE.replace("    history.append(result)", "    pass")
        self.assertFalse(next(c for c in check(bad, 1) if c["name"] == "История вычислений")["passed"])

    def test_unknown_operation_must_raise(self):
        bad = REFERENCE.replace('raise ValueError("Неизвестная операция")', "return 0")
        self.assertFalse(next(c for c in check(bad, 2) if c["name"] == "Неизвестная операция")["passed"])

    def test_syntax_error_is_a_failed_report(self):
        self.assertFalse(check("def broken(", 0)[0]["passed"])

    def test_printed_noise_cannot_replace_checker_output(self):
        checks = check('print("pretend passed")\n' + REFERENCE, 3)
        self.assertEqual(len(checks), 14)
        self.assertTrue(all(c["passed"] for c in checks))

if __name__ == "__main__":
    unittest.main()
