"""2026-10-26 · Codex：按配置价格生成并复核双方精确同预算场景。"""
import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parent
CATALOG = ROOT / "config/point-buy.json"
CREATURES = ROOT / "engine/Mods/cultivation/Content/config/creatures.json"
SPELLS = ROOT / "engine/Mods/cultivation/Content/config/spells.json"
SKILLS = ROOT / "engine/Mods/cultivation/Content/config/skills.json"
SCHOOLS = ("sword", "body", "demon", "talisman")
REALMS = ("Qi", "Foundation", "Core", "Soul", "Deity")


def load_prices():
    prices = json.loads(CATALOG.read_text())
    creatures = json.loads(CREATURES.read_text())
    spells = json.loads(SPELLS.read_text())
    prices["technique_requirements"] = {
        f"cultivation:{name}": node["levels"]["base"]["battleEffects"]["00Technique"]
        for name, node in spells.items() if "00Technique" in node["levels"]["base"]["battleEffects"]
    }
    prices["skill_spells"] = {rule["requiredSkill"]: spell for spell, rule in prices["technique_requirements"].items() if "requiredSkill" in rule}
    fingerprint = hashlib.sha256(b"\0".join(path.read_bytes() for path in (CATALOG, CREATURES, SPELLS, SKILLS))).hexdigest()
    return prices, creatures, fingerprint


def spell_unlocked(spell, commander, prices, creatures, skills=None):
    requirement = prices["technique_requirements"].get(spell)
    if requirement is None:
        return True
    body = creatures[commander.removeprefix("cultivation:")]
    if skills is not None and "requiredSkill" in requirement:
        if not any(skill["skill"] == requirement["requiredSkill"] for skill in skills):
            return False
    return (commander.startswith(requirement["bodyPrefix"])
            and body["abilities"]["realm"]["val"] >= requirement["minimumRealm"])


def integer(value, name, minimum=0, maximum=100000):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f"{name} 必须为 {minimum}..{maximum} 的整数")
    return value


def skill_unlocked(skill, commander, prices, creatures):
    granted = prices["skill_spells"].get(skill)
    if granted:
        return spell_unlocked(granted, commander, prices, creatures)
    requirement = prices.get("skill_requirements", {}).get(skill)
    if requirement is None:
        return True
    return (commander.startswith(requirement["bodyPrefix"])
            and creatures[commander.removeprefix("cultivation:")]["abilities"]["realm"]["val"] >= requirement["minimumRealm"])


def price_slot(slot, prices, creatures):
    allowed = {"selectedHero", "commander", "selectedArmy", "primSkillLevel", "secSkillLevel",
               "mana", "spellBook", "spells", "artifacts", "warMachines"}
    if set(slot) - allowed:
        raise ValueError("场景含未计价字段")
    hero = slot["selectedHero"]
    school = next((school for school in SCHOOLS if hero == f"cultivation:{school}Master"), None)
    body = slot["commander"].removeprefix("cultivation:")
    if school is None or not slot["commander"].startswith("cultivation:") or body not in {school + realm for realm in REALMS}:
        raise ValueError("主英雄与肉身流派不一致或未计价")
    if slot.get("warMachines", False):
        raise ValueError("战争机器尚未计价")
    breakdown = {"body": creatures[body]["cost"]["gold"]}
    primary = slot["primSkillLevel"]
    if len(primary) != 4:
        raise ValueError("必须显式给出四项主属性")
    breakdown["primary"] = sum(integer(v, "主属性", maximum=20) for v in primary) * prices["primary_point"]
    breakdown["mana"] = integer(slot["mana"], "灵力", maximum=200) * prices["mana_point"]
    if type(slot["spellBook"]) is not bool:
        raise ValueError("spellBook 必须为布尔值")
    breakdown["spellbook"] = prices["spellbook"] if slot["spellBook"] else 0
    spells = slot.get("spells", [])
    if len(set(spells)) != len(spells) or (spells and not slot["spellBook"]):
        raise ValueError("法术重复或缺少法术书")
    if any(not spell_unlocked(spell, slot["commander"], prices, creatures, slot.get("secSkillLevel", [])) for spell in spells):
        raise ValueError("神通不满足流派或境界解锁条件")
    breakdown["spells"] = sum(prices["spells"][spell] for spell in spells)
    skills = slot.get("secSkillLevel", [])
    if len(skills) > 8 or len({s["skill"] for s in skills}) != len(skills):
        raise ValueError("副技能重复或超过八项")
    for skill in skills:
        if not skill_unlocked(skill["skill"], slot["commander"], prices, creatures):
            raise ValueError("功法不满足流派或境界条件")
    breakdown["skills"] = sum(prices["skills"][s["skill"]][("basic", "advanced", "expert").index(s["masteryLevel"])] for s in skills)
    artifacts = slot.get("artifacts", {})
    if len(set(artifacts.values())) != len(artifacts):
        raise ValueError("法宝装备槽冲突")
    for artifact, position in artifacts.items():
        if position != prices["artifacts"][artifact]["position"]:
            raise ValueError("法宝装备槽不匹配")
    breakdown["artifacts"] = sum(prices["artifacts"][a]["points"] for a in artifacts)
    army = slot["selectedArmy"]
    if not 1 <= len(army) <= 7:
        raise ValueError("军队必须为一至七队")
    breakdown["army"] = 0
    for stack in army:
        creature = creatures[stack["type"].removeprefix("cultivation:")]
        if "heroBody" in creature["abilities"] or stack["type"] not in prices["rosters"][school]:
            raise ValueError("军队槽不能购买额外英雄或未计价兵种")
        breakdown["army"] += integer(stack["amount"], "人数", minimum=1) * creature["cost"]["gold"]
    return {"total": sum(breakdown.values()), "items": breakdown}


def audit(scenario):
    if set(scenario) - {"selectedTerrain", "slots", "point_buy"}:
        raise ValueError("预算场景含未支持的顶层字段")
    prices, creatures, fingerprint = load_prices()
    metadata = scenario["point_buy"]
    budget = integer(metadata["budget"], "预算", minimum=1)
    if metadata["prices_sha256"] != fingerprint:
        raise ValueError("计价配置已改变，需要重新生成预算场景")
    if len(scenario["slots"]) != 2:
        raise ValueError("需要双方场景")
    costs = [price_slot(slot, prices, creatures) for slot in scenario["slots"]]
    if any(cost["total"] != budget for cost in costs):
        raise ValueError(f"双方必须精确花费 {budget} 点：实际为 {[cost['total'] for cost in costs]}")
    return {"budget": budget, "sides": costs, "prices_sha256": fingerprint}


def generate(budget, schools=("sword", "body"), realm="Core", seed=1, varied_loadout=False):
    integer(budget, "预算", minimum=1)
    prices, creatures, fingerprint = load_prices()
    realms = (realm, realm) if isinstance(realm, str) else tuple(realm)
    if len(realms) != 2 or any(r not in REALMS for r in realms) or len(schools) != 2 or any(s not in SCHOOLS for s in schools):
        raise ValueError("无效流派或境界")
    rng = random.Random(seed)
    slots = []
    for school, realm in zip(schools, realms):
        troops = {name.removeprefix("cultivation:"): creatures[name.removeprefix("cultivation:")]["cost"]["gold"]
                  for name in prices["rosters"][school]}
        slot = {"selectedHero": f"cultivation:{school}Master", "commander": f"cultivation:{school}{realm}",
                "selectedArmy": [], "primSkillLevel": [0, 0, 2, 2], "secSkillLevel": [],
                "mana": 20, "spellBook": True, "spells": ["core:magicArrow"], "artifacts": {}, "warMachines": False}
        # 用一名士兵满足计价接口，再取回该兵成本计算可用于军队的余额。
        first = next(iter(troops))
        slot["selectedArmy"] = [{"type": "cultivation:" + first, "amount": 1}]
        remaining = budget - price_slot(slot, prices, creatures)["total"] + troops[first]
        if remaining < min(troops.values()):
            raise ValueError("预算不足以支付肉身、法术配置和至少一名士兵")
        reachable = [False] * (remaining + 1)
        reachable[0] = True
        for total in range(1, remaining + 1):
            reachable[total] = any(total >= cost and reachable[total - cost] for cost in troops.values())
        if not reachable[remaining]:
            raise ValueError("现有兵种价格无法精确花完此预算")
        if varied_loadout:
            for category in ("skills", "artifacts", "spells"):
                if not rng.choice((False, True)):
                    continue
                candidate = copy.deepcopy(slot)
                choices = sorted(prices[category])
                if category == "spells":
                    choices = [name for name in choices if spell_unlocked(name, slot["commander"], prices, creatures, slot["secSkillLevel"])]
                elif category == "skills":
                    choices = [name for name in choices if skill_unlocked(name, slot["commander"], prices, creatures)]
                name = rng.choice(choices)
                if category == "skills":
                    candidate["secSkillLevel"] = [{"skill": name, "masteryLevel": rng.choice(("basic", "advanced", "expert"))}]
                elif category == "artifacts":
                    candidate["artifacts"] = {name: prices[category][name]["position"]}
                elif name not in candidate["spells"]:
                    candidate["spells"].append(name)
                extra = price_slot(candidate, prices, creatures)["total"] - price_slot(slot, prices, creatures)["total"]
                if min(troops.values()) <= remaining - extra and reachable[remaining - extra]:
                    slot = candidate
                    remaining -= extra
        army = Counter()
        while remaining:
            choices = [name for name, cost in troops.items() if cost <= remaining and reachable[remaining - cost]]
            name = rng.choice(choices)
            army[name] += 1
            remaining -= troops[name]
        slot["selectedArmy"] = [{"type": f"cultivation:{name}", "amount": count} for name, count in sorted(army.items())]
        slots.append(slot)
    scenario = {"selectedTerrain": "core:sand", "slots": slots,
                "point_buy": {"budget": budget, "seed": seed, "prices_sha256": fingerprint}}
    audit(scenario)
    return scenario


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--budget", type=int, required=True)
    parser.add_argument("--schools", nargs=2, choices=SCHOOLS, default=["sword", "body"])
    parser.add_argument("--realm", choices=REALMS, default="Core")
    parser.add_argument("--realms", nargs=2, choices=REALMS, help="分别指定双方境界，覆盖 --realm")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--varied-loadout", action="store_true", help="同时随机购买已计价的副技能、法宝和法术")
    args = parser.parse_args()
    scenario = generate(args.budget, args.schools, args.realms or args.realm, args.seed, args.varied_loadout)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(scenario, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(audit(scenario), ensure_ascii=False))


if __name__ == "__main__":
    main()
