"""2026-10-26 · Codex：预算生成、原生对战、指标报告的完整链路。"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from pointbuy import audit, generate

ROOT = Path(__file__).resolve().parents[1]


class RunnerTests(unittest.TestCase):
    def test_budgeted_native_battles_produce_reaggregatable_metrics(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            scenario = generate(5000, seed=42, varied_loadout=True)
            audit(scenario)
            source = directory / "input.json"
            source.write_text(json.dumps(scenario))
            output = directory / "run"
            subprocess.run([sys.executable, str(ROOT / "simulate.py"), "--scenario", str(source),
                            "--output", str(output), "--count", "3", "--seed", "42"],
                           check=True, capture_output=True, timeout=60)
            report = json.loads((output / "metrics.json").read_text())
            self.assertEqual(report["completed"], 3)
            self.assertTrue(report["equal_budget_verified"])
            self.assertEqual([s["total"] for s in report["point_buy"]["sides"]], [5000, 5000])
            self.assertEqual((output / "scenario.json").read_bytes(), source.read_bytes())
            self.assertEqual(report["results_sha256"], hashlib.sha256((output / "battles.jsonl").read_bytes()).hexdigest())
            recheck = directory / "recheck"
            subprocess.run([sys.executable, str(ROOT / "simulate.py"), "--input", str(output / "battles.jsonl"),
                            "--output", str(recheck)], check=True, capture_output=True, timeout=10)
            second = json.loads((recheck / "metrics.json").read_text())
            for key in ("hero_damage_share", "by_hero", "decapitation", "average_rounds", "hero_outcomes"):
                self.assertEqual(report[key], second[key])
            self.assertFalse(second["equal_budget_verified"])


if __name__ == "__main__":
    unittest.main()
