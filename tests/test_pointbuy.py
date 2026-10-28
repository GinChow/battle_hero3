"""2026-10-26 · Codex：精确预算、确定性和未计价项目校验。"""
import copy
import unittest

from pointbuy import audit, generate, load_prices, price_slot


class PointBuyTests(unittest.TestCase):
    def test_sect_rosters_are_distinct_and_summons_cannot_be_bought(self):
        prices, creatures, _ = load_prices()
        for schools in (("sword", "body"), ("demon", "talisman")):
            scenario = generate(10000, schools, varied_loadout=True)
            for school, slot in zip(schools, scenario["slots"]):
                self.assertTrue(all(stack["type"] in prices["rosters"][school] for stack in slot["selectedArmy"]))
                for invalid in ("cultivation:bloodPuppet", "cultivation:talismanSoldier", prices["rosters"]["body" if school != "body" else "sword"][0]):
                    changed = copy.deepcopy(slot)
                    changed["selectedArmy"][0]["type"] = invalid
                    with self.assertRaises(ValueError):
                        price_slot(changed, prices, creatures)

    def test_new_arts_require_their_school_and_pay_for_all_ranks(self):
        prices, creatures, _ = load_prices()
        for school, arts in {"sword": ("swordEscapeArt", "swordCloneArt", "swordIntentArt"),
                            "demon": ("demonBloodArt", "evilWindArt", "bloodDrainArt"),
                            "talisman": ("talismanSoldierArt", "thunderTalismanArt", "purifyTalismanArt")}.items():
            slot, other = generate(10000, (school, "body"))["slots"]
            for art in arts:
                for rank, cost in zip(("basic", "advanced", "expert"), (250, 500, 800)):
                    skill = [{"skill": "cultivation:" + art, "masteryLevel": rank}]
                    slot["secSkillLevel"] = skill
                    self.assertEqual(price_slot(slot, prices, creatures)["total"], 10000 + cost)
                    other["secSkillLevel"] = skill
                    with self.assertRaises(ValueError):
                        price_slot(other, prices, creatures)

    def test_exact_budget_reproducible_and_has_one_body_per_side(self):
        for seed in range(20):
            scenario = generate(5000, seed=seed)
            self.assertEqual(scenario, generate(5000, seed=seed))
            self.assertEqual([side["total"] for side in audit(scenario)["sides"]], [5000, 5000])
            for slot in scenario["slots"]:
                self.assertLessEqual(len(slot["selectedArmy"]), 7)
                self.assertGreater(len(slot["selectedArmy"]), 0)
                self.assertTrue(all(stack["amount"] > 0 for stack in slot["selectedArmy"]))
        self.assertNotEqual(generate(5000, seed=1), generate(5000, seed=2))

    def test_all_realms_and_schools_can_be_priced(self):
        for realm in ("Qi", "Foundation", "Core", "Soul", "Deity"):
            scenario = generate(10000, ("demon", "talisman"), realm)
            self.assertEqual(audit(scenario)["budget"], 10000)

    def test_higher_realm_competes_with_army_for_same_budget(self):
        scenario = generate(5000, realm=("Qi", "Deity"))
        low, high = audit(scenario)["sides"]
        self.assertEqual(low["total"], high["total"])
        self.assertEqual(high["items"]["body"] - low["items"]["body"], 1200)
        self.assertEqual(low["items"]["army"] - high["items"]["army"], 1200)

    def test_varied_loadouts_spend_exact_budget(self):
        purchased = set()
        for seed in range(20):
            scenario = generate(5000, seed=seed, varied_loadout=True)
            audit(scenario)
            self.assertEqual(scenario, generate(5000, seed=seed, varied_loadout=True))
            for slot in scenario["slots"]:
                for name in ("secSkillLevel", "artifacts"):
                    if slot[name]:
                        purchased.add(name)
                if len(slot["spells"]) > 1:
                    purchased.add("spells")
        self.assertEqual(purchased, {"secSkillLevel", "artifacts", "spells"})

    def test_changes_cannot_hide_extra_troops_or_second_body(self):
        scenario = generate(5000)
        scenario["slots"][0]["selectedArmy"][0]["amount"] += 1
        with self.assertRaises(ValueError):
            audit(scenario)
        scenario = generate(5000)
        scenario["slots"][0]["selectedArmy"][0]["type"] = "cultivation:swordQi"
        with self.assertRaises(ValueError):
            audit(scenario)

    def test_skill_and_artifact_prices_are_included(self):
        prices, creatures, _ = load_prices()
        slot = generate(5000)["slots"][0]
        base = price_slot(slot, prices, creatures)["total"]
        slot["secSkillLevel"] = [{"skill": "core:offence", "masteryLevel": "expert"}]
        slot["artifacts"] = {"core:centaurAxe": 3}
        self.assertEqual(price_slot(slot, prices, creatures)["total"] - base, 1150)

    def test_unpriced_fields_negative_numbers_and_stale_prices_rejected(self):
        original = generate(5000)
        for update in ({"mana": -1}, {"warMachines": True}, {"unknown": 1}):
            scenario = copy.deepcopy(original)
            scenario["slots"][0].update(update)
            with self.assertRaises(ValueError):
                audit(scenario)
        original["point_buy"]["prices_sha256"] = "changed"
        with self.assertRaises(ValueError):
            audit(original)

    def test_impossible_budgets_fail_instead_of_silently_underspending(self):
        for budget in (100, 1801, 5001):
            with self.assertRaises(ValueError):
                generate(budget)

    def test_technique_unlock_is_part_of_budget_validation(self):
        prices, creatures, _ = load_prices()
        scenario = generate(5000)
        sword, body = scenario["slots"]
        sword["spells"].append("cultivation:swordStorm")
        self.assertEqual(price_slot(sword, prices, creatures)["total"], 5500)
        body["spells"].append("cultivation:swordStorm")
        with self.assertRaises(ValueError):
            price_slot(body, prices, creatures)
        sword["commander"] = "cultivation:swordFoundation"
        with self.assertRaises(ValueError):
            price_slot(sword, prices, creatures)

    def test_ranked_technique_is_paid_by_skill_and_cannot_be_obtained_free(self):
        prices, creatures, _ = load_prices()
        sword, body = generate(5000)["slots"]
        body["spells"].append("cultivation:groundShock")
        with self.assertRaises(ValueError):
            price_slot(body, prices, creatures)
        for rank, cost in (("basic", 250), ("advanced", 500), ("expert", 800)):
            body["secSkillLevel"] = [{"skill": "cultivation:earthShakingArt", "masteryLevel": rank}]
            self.assertEqual(price_slot(body, prices, creatures)["total"], 5000 + cost)
        sword["secSkillLevel"] = body["secSkillLevel"]
        with self.assertRaises(ValueError):
            price_slot(sword, prices, creatures)

    def test_diamond_art_requires_body_domain_and_pays_per_rank(self):
        prices, creatures, _ = load_prices()
        sword, body = generate(5000, realm="Soul")["slots"]
        for rank, cost in (("basic", 300), ("advanced", 600), ("expert", 900)):
            body["secSkillLevel"] = [{"skill": "cultivation:diamondArt", "masteryLevel": rank}]
            self.assertEqual(price_slot(body, prices, creatures)["total"], 5000 + cost)
        sword["secSkillLevel"] = body["secSkillLevel"]
        with self.assertRaises(ValueError):
            price_slot(sword, prices, creatures)
        body["commander"] = "cultivation:bodyCore"
        with self.assertRaises(ValueError):
            price_slot(body, prices, creatures)
        body["commander"] = "cultivation:bodySoul"
        body["secSkillLevel"] = [
            {"skill": f"cultivation:{name}", "masteryLevel": "expert"}
            for name in ("earthShakingArt", "diamondArt", "guardArt")
        ]
        self.assertEqual(price_slot(body, prices, creatures)["total"], 7350)


if __name__ == "__main__":
    unittest.main()
