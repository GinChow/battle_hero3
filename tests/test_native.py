"""2026-10-26 · Codex：对真实 VCMI 可执行程序进行本地功能验证。"""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "build" / "bin"
SCENARIO = ROOT / "scenarios" / "native-smoke.json"


class NativeBattleTests(unittest.TestCase):
    def test_ai_hero_spells_only_happen_on_own_body_turn(self):
        for scenario in ("sword-vs-body.json", "demon-vs-talisman.json"):
            for row in self.run_battles(count=2, scenario=ROOT / "scenarios" / scenario):
                self.assertEqual(row["status"], "completed")
                bodies = {unit["side"]: unit["id"] for unit in row["units_initial"] if unit["hero_body"]}
                spells = [spell for spell in row["spells"] if spell["hero"]]
                self.assertTrue(spells)
                for spell in spells:
                    self.assertEqual(spell["active_unit"], bodies[spell["side"]])

    def run_battles(self, seed=42, count=3, rounds=100, scenario=SCENARIO):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "results.jsonl"
            process = subprocess.run(
                [str(BIN / "battle_sim"), str(scenario), str(output),
                 str(seed), str(count), str(rounds)],
                cwd=BIN, capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(process.returncode, 0, process.stderr)
            return [json.loads(line) for line in output.read_text().splitlines()]

    def test_native_battles_finish_and_repeat(self):
        first = self.run_battles()
        self.assertEqual(first, self.run_battles())
        self.assertEqual([row["seed"] for row in first], [42, 43, 44])
        for row in first:
            self.assertEqual(row["engine"], "VCMI")
            self.assertEqual(row["status"], "completed")
            self.assertIn(row["winner"], (-1, 0, 1))
            self.assertGreater(row["actions"], 0)
            self.assertEqual(row["actions"], len(row["events"]))

    def test_damage_events_conserve_health_and_attribute_counters(self):
        for row in self.run_battles():
            units = {unit["id"]: unit for unit in row["units_initial"]}
            final = {unit["id"]: unit for unit in row["units_final"]}
            losses = {unit: 0 for unit in units}
            self.assertTrue(row["damage_events"])
            self.assertTrue(any(event["kind"] == "counter" for event in row["damage_events"]))
            for index, event in enumerate(row["damage_events"]):
                self.assertEqual(event["sequence"], index)
                self.assertEqual(event["source_side"], units[event["source"]]["side"])
                self.assertFalse(event["hero_damage"])
                self.assertEqual(event["damage"], event["health_before"] - event["health_after"])
                self.assertEqual(event["killed"], event["count_before"] - event["count_after"])
                self.assertLessEqual(event["damage"], event["health_before"])
                losses[event["target"]] += event["damage"]
            for unit in units:
                self.assertEqual(losses[unit], units[unit]["health"] - final[unit]["health"])

    def test_round_limit_is_not_reported_as_victory(self):
        result, = self.run_battles(count=1, rounds=1)
        self.assertEqual(result["status"], "round_limit")
        self.assertNotIn("winner", result)

    def test_cultivation_battles_finish_and_repeat(self):
        scenario = ROOT / "scenarios" / "cultivation-smoke.json"
        results = self.run_battles(scenario=scenario)
        self.assertEqual(results, self.run_battles(scenario=scenario))
        for row in results:
            self.assertEqual(row["status"], "completed")
            self.assertEqual(sum(unit["hero_body"] for unit in row["units_initial"]), 2)

    def test_hero_bodies_and_spells_coexist(self):
        results = self.run_battles(scenario=ROOT / "scenarios" / "hero-body-smoke.json")

        self.assertEqual(results, self.run_battles(scenario=ROOT / "scenarios" / "hero-body-smoke.json"))
        for row in results:
            bodies = [unit for unit in row["units_initial"] if unit["hero_body"]]
            self.assertEqual(len(bodies), 2)
            self.assertEqual({body["side"] for body in bodies}, {0, 1})
            body_ids = {body["id"] for body in bodies}
            self.assertTrue(any(event["unit"] in body_ids for event in row["events"]))
            self.assertTrue(any(event["hero"] for event in row["spells"]))
            spell_damage = [event for event in row["damage_events"] if event["kind"] == "spell"]
            self.assertTrue(spell_damage)
            for event in spell_damage:
                self.assertTrue(event["hero_damage"])
                self.assertIn(event["source_side"], (0, 1))
                self.assertEqual(event["source"], -1)
                self.assertEqual(event["spell"], "core:magicArrow")
            self.assertTrue(all(0 <= value <= 20 for value in row["mana_remaining"]))
            self.assertEqual(row["status"], "completed")

    def test_explicit_empty_mana_is_not_refilled(self):
        with tempfile.TemporaryDirectory() as directory:
            node = json.loads((ROOT / "scenarios" / "hero-body-smoke.json").read_text())
            for side in node["slots"]:
                side["mana"] = 0
            scenario = Path(directory) / "empty-mana.json"
            scenario.write_text(json.dumps(node))
            result, = self.run_battles(count=1, scenario=scenario)
            self.assertFalse(result["spells"])
            self.assertEqual(result["mana_remaining"], [0, 0])

    def test_ai_uses_sword_storm_with_cooldown_and_attribution(self):
        results = self.run_battles(scenario=ROOT / "scenarios" / "sword-storm.json")
        repeated = False
        for row in results:
            self.assertEqual(row["status"], "completed")
            casts = [event for event in row["spells"] if event["spell"] == "cultivation:swordStorm"]
            self.assertTrue(casts)
            repeated |= len(casts) > 1
            for first, second in zip(casts, casts[1:]):
                self.assertGreaterEqual(second["round"] - first["round"], 3)
            self.assertEqual(row["mana_remaining"][0], 64 - 16 * len(casts))
            damage = [event for event in row["damage_events"] if event["spell"] == "cultivation:swordStorm"]
            self.assertTrue(damage)
            self.assertTrue(all(event["hero_damage"] and event["source_side"] == 0 and event["target_side"] == 1 for event in damage))
        self.assertTrue(repeated, "至少一场应验证AI在冷却结束后再次施法")

    def test_ai_uses_spell_granted_by_ranked_cultivation_skill(self):
        results = self.run_battles(scenario=ROOT / "scenarios" / "body-shock.json")
        repeated = False
        for row in results:
            self.assertEqual(row["status"], "completed")
            casts = [event for event in row["spells"] if event["spell"] == "cultivation:groundShock"]
            self.assertTrue(casts)
            repeated |= len(casts) > 1
            self.assertEqual(row["mana_remaining"][0], 60 - 12 * len(casts))
            for first, second in zip(casts, casts[1:]):
                self.assertGreaterEqual(second["round"] - first["round"], 2)
        self.assertTrue(repeated)

    def test_three_body_arts_coexist_in_native_battle(self):
        with tempfile.TemporaryDirectory() as directory:
            scenario = json.loads((ROOT / "scenarios" / "body-shock.json").read_text())
            scenario["slots"][0]["commander"] = "cultivation:bodySoul"
            scenario["slots"][0]["secSkillLevel"] = [
                {"skill": f"cultivation:{name}", "masteryLevel": "expert"}
                for name in ("earthShakingArt", "diamondArt", "guardArt")
            ]
            path = Path(directory) / "three-arts.json"
            path.write_text(json.dumps(scenario))
            result, = self.run_battles(count=1, scenario=path)
            self.assertEqual(result["status"], "completed")
            self.assertTrue(any(event["spell"] == "cultivation:groundShock" for event in result["spells"]))

    def test_zero_count_fails_without_writing_results(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.jsonl"
            process = subprocess.run(
                [str(BIN / "battle_sim"), str(SCENARIO), str(output), "42", "0"],
                cwd=BIN, capture_output=True, text=True, timeout=10,
            )
            self.assertNotEqual(process.returncode, 0)
            self.assertFalse(output.exists())

    def test_missing_army_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            node = json.loads(SCENARIO.read_text())
            node["slots"][0]["selectedArmy"] = []
            scenario = Path(directory) / "empty.json"
            scenario.write_text(json.dumps(node))
            output = Path(directory) / "result.jsonl"
            process = subprocess.run(
                [str(BIN / "battle_sim"), str(scenario), str(output)],
                cwd=BIN, capture_output=True, text=True, timeout=20,
            )
            self.assertNotEqual(process.returncode, 0)
            self.assertIn("require an army", process.stderr)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
