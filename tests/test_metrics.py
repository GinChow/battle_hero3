"""2026-10-26 · Codex：独立样本校验统计分母、重生与来源缺失。"""
import copy
import unittest

from simulate import aggregate, final_body_outcomes


def hit(target=1, source=0, damage=100, hero=True, sequence=0, packet=10):
    return {"target": target, "source_side": source, "target_side": target,
            "damage": damage, "hero_damage": hero, "target_clone": False,
            "health_before": damage, "health_after": 0, "killed": 1,
            "round": 3, "sequence": sequence, "packet": packet}


def battle():
    return {"schema": 3, "seed": 42, "status": "completed", "winner": 0,
            "heroes": ["sword", "body"], "rounds": 5,
            "units_initial": [{"id": 0, "side": 0, "hero_body": True, "health": 100},
                              {"id": 1, "side": 1, "hero_body": True, "health": 100}],
            "units_final": [{"id": 0, "health": 40}, {"id": 1, "health": 0}],
            "damage_events": [hit(damage=30), hit(damage=70, hero=False, sequence=1)]}


class MetricTests(unittest.TestCase):
    def test_damage_share_excludes_friendly_fire_and_illusions(self):
        row = battle()
        friendly = hit(target=0, source=0, damage=500)
        clone = hit(damage=1000)
        clone["target_clone"] = True
        row["damage_events"] += [friendly, clone]
        report = aggregate([row])
        self.assertEqual(report["damage"], 100)
        self.assertEqual(report["hero_damage_share"], 0.3)
        self.assertEqual(report["friendly_damage_excluded"], 500)
        self.assertEqual(report["clone_damage_excluded"], 1000)

    def test_timeouts_do_not_enter_win_survival_or_round_denominators(self):
        win = battle()
        loss = copy.deepcopy(win)
        loss.update(winner=1, rounds=7)
        draw = copy.deepcopy(win)
        draw.update(winner=-1, rounds=9)
        timeout = copy.deepcopy(win)
        timeout.update(status="round_limit", rounds=101)
        del timeout["winner"]
        report = aggregate([win, loss, draw, timeout])
        self.assertEqual(report["completed"], 3)
        self.assertEqual(report["average_rounds"], 7)
        self.assertEqual(report["by_hero"]["sword"]["win_rate"], 1 / 3)
        self.assertEqual(report["by_hero"]["sword"]["hero_survival_rate"], 1)
        self.assertEqual(report["decapitation"]["samples"], 3)
        self.assertEqual(report["decapitation"]["win_rate"], 1 / 3)

    def test_successful_rebirth_is_not_final_death(self):
        row = battle()
        row["units_final"][1]["health"] = 50
        report = aggregate([row])
        self.assertEqual(report["decapitation"]["samples"], 0)
        self.assertIsNone(report["decapitation"]["win_rate"])
        self.assertTrue(final_body_outcomes(row)[1]["alive"])

    def test_last_lethal_hit_after_rebirth_determines_death_round(self):
        row = battle()
        final_hit = hit(sequence=2, packet=20)
        final_hit["round"] = 5
        row["damage_events"].append(final_hit)
        outcome = final_body_outcomes(row)[1]
        self.assertEqual(outcome["death_round"], 5)
        self.assertEqual(outcome["death_sequence"], 2)

    def test_same_packet_deaths_are_not_assigned_a_first_killer(self):
        row = battle()
        row["units_final"][0]["health"] = 0
        row["damage_events"] = [hit(sequence=0), hit(target=0, source=1, sequence=1)]
        report = aggregate([row])
        self.assertEqual(report["decapitation"]["samples"], 0)
        self.assertEqual(report["decapitation"]["excluded"]["same_packet_deaths"], 1)

    def test_unknown_source_withholds_damage_share(self):
        row = battle()
        row["damage_events"][0]["source_side"] = -1
        report = aggregate([row])
        self.assertFalse(report["attribution_complete"])
        self.assertEqual(report["unattributed_damage"], 30)
        self.assertIsNone(report["hero_damage_share"])

    def test_missing_lethal_event_is_reported(self):
        row = battle()
        row["damage_events"] = []
        report = aggregate([row])
        self.assertEqual(report["decapitation"]["excluded"]["missing_death_event"], 1)

    def test_old_schema_and_invalid_damage_are_rejected(self):
        row = battle()
        row["schema"] = 2
        with self.assertRaises(ValueError):
            aggregate([row])
        row["schema"] = 3
        row["damage_events"][0]["damage"] = 1000
        with self.assertRaises(ValueError):
            aggregate([row])

    def test_empty_dataset_has_no_invented_rates(self):
        report = aggregate([])
        self.assertIsNone(report["average_rounds"])
        self.assertIsNone(report["hero_damage_share"])
        self.assertIsNone(report["decapitation"]["win_rate"])


if __name__ == "__main__":
    unittest.main()
