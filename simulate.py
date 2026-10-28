"""2026-10-26 · Codex：原生批量运行与战斗指标聚合，使用 Python 标准库。"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import subprocess

from pointbuy import audit

ROOT = Path(__file__).resolve().parent


def fraction(numerator, denominator):
    return numerator / denominator if denominator else None


def wilson(wins, count):
    if not count:
        return None
    z = 1.959963984540054
    p = wins / count
    denominator = 1 + z * z / count
    center = (p + z * z / (2 * count)) / denominator
    margin = z * ((p * (1 - p) + z * z / (4 * count)) / count) ** 0.5 / denominator
    return [max(0, center - margin), min(1, center + margin)]


def final_body_outcomes(row):
    """重生后仍活着不算遁逃；最终死亡匹配最后一次致死包。"""
    final = {unit["id"]: unit for unit in row["units_final"]}
    outcomes = []
    for body in row["units_initial"]:
        if not body["hero_body"]:
            continue
        unit = final.get(body["id"])
        alive = unit is not None and unit["health"] > 0
        lethal = None
        if not alive:
            lethal = next((event for event in reversed(row["damage_events"] or [])
                           if event["target"] == body["id"] and event["health_before"] > 0
                           and event["health_after"] == 0), None)
        outcomes.append({"side": body["side"], "unit": body["id"], "alive": alive,
                         "death_round": lethal["round"] if lethal else None,
                         "death_sequence": lethal["sequence"] if lethal else None,
                         "death_packet": lethal["packet"] if lethal else None,
                         "killer_side": lethal["source_side"] if lethal else None})
    return outcomes


def aggregate(rows):
    groups = defaultdict(Counter)
    totals = Counter()
    statuses = Counter()
    decap_excluded = Counter()
    outcomes = []
    for row in rows:
        if row.get("schema") != 3 or len(row.get("heroes", [])) != 2:
            raise ValueError("需要 schema=3 且包含 heroes 的原生结果；请重新运行旧数据")
        statuses[row["status"]] += 1
        if row["status"] != "completed":
            continue
        winner = row["winner"]
        if winner not in (-1, 0, 1):
            raise ValueError("无效的 winner")
        totals["completed"] += 1
        totals["rounds"] += row["rounds"]
        totals["draws"] += winner == -1
        side_damage = [Counter(), Counter()]
        for event in row["damage_events"] or []:
            damage = event["damage"]
            if damage < 0 or damage != event["health_before"] - event["health_after"]:
                raise ValueError("伤害事件不满足生命差守恒")
            if event["target_clone"]:
                totals["clone_damage_excluded"] += damage
                continue
            side = event["source_side"]
            if side not in (0, 1):
                totals["unattributed_damage"] += damage
                continue
            if side == event["target_side"]:
                totals["friendly_damage_excluded"] += damage
                continue
            side_damage[side]["damage"] += damage
            side_damage[side]["hero_damage"] += damage if event["hero_damage"] else 0
            side_damage[side]["kills"] += event["killed"]
        bodies = final_body_outcomes(row)
        outcomes.append({"seed": row["seed"], "heroes": row["heroes"], "bodies": bodies})
        for side in (0, 1):
            group = groups[row["heroes"][side]]
            group["appearances"] += 1
            group["wins"] += winner == side
            group["draws"] += winner == -1
            group["losses"] += winner == 1 - side
            group.update(side_damage[side])
            totals.update(side_damage[side])
        for body in bodies:
            group = groups[row["heroes"][body["side"]]]
            group["bodies"] += 1
            group["surviving_bodies"] += body["alive"]
        dead = [body for body in bodies if not body["alive"]]
        if not dead:
            decap_excluded["no_final_body_death"] += 1
        elif any(body["death_sequence"] is None for body in dead):
            decap_excluded["missing_death_event"] += 1
        else:
            dead.sort(key=lambda body: body["death_sequence"])
            first = dead[0]
            if len(dead) > 1 and first["death_packet"] == dead[1]["death_packet"]:
                decap_excluded["same_packet_deaths"] += 1
            elif first["killer_side"] != 1 - first["side"]:
                decap_excluded["not_enemy_kill"] += 1
            else:
                totals["decap_samples"] += 1
                totals["decap_wins"] += winner == first["killer_side"]
    attribution_complete = totals["unattributed_damage"] == 0
    report_groups = {}
    for name, group in sorted(groups.items()):
        report_groups[name] = dict(group)
        report_groups[name].update({
            "win_rate": fraction(group["wins"], group["appearances"]),
            "win_rate_95ci": wilson(group["wins"], group["appearances"]),
            "hero_damage_share": fraction(group["hero_damage"], group["damage"]) if attribution_complete else None,
            "hero_survival_rate": fraction(group["surviving_bodies"], group["bodies"]),
        })
    return {
        "schema": 1, "statuses": dict(statuses), "completed": totals["completed"],
        "draws": totals["draws"], "average_rounds": fraction(totals["rounds"], totals["completed"]),
        "damage": totals["damage"], "hero_damage": totals["hero_damage"],
        "hero_damage_share": fraction(totals["hero_damage"], totals["damage"]) if attribution_complete else None,
        "attribution_complete": attribution_complete, "unattributed_damage": totals["unattributed_damage"],
        "friendly_damage_excluded": totals["friendly_damage_excluded"],
        "clone_damage_excluded": totals["clone_damage_excluded"],
        "decapitation": {"samples": totals["decap_samples"], "wins": totals["decap_wins"],
                         "win_rate": fraction(totals["decap_wins"], totals["decap_samples"]),
                         "win_rate_95ci": wilson(totals["decap_wins"], totals["decap_samples"]),
                         "excluded": dict(decap_excluded)},
        "by_hero": report_groups, "hero_outcomes": outcomes,
        "equal_budget_verified": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", type=Path)
    parser.add_argument("--input", type=Path, help="仅聚合已有 JSONL，与 --scenario 二选一")
    parser.add_argument("--output", type=Path, help="批量模式结果目录")
    parser.add_argument("--play", action="store_true", help="打开游戏窗口，手动控制双方战斗")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--rounds", type=int, default=100)
    parser.add_argument("--binary", type=Path, default=ROOT / "build/bin/battle_sim")
    args = parser.parse_args()
    if (args.scenario is None) == (args.input is None):
        parser.error("必须且只能指定 --scenario 或 --input")
    if args.play:
        if args.scenario is None:
            parser.error("--play 需要 --scenario")
        scenario_path = args.scenario.resolve()
        scenario = json.loads(scenario_path.read_text())
        if "point_buy" in scenario:
            audit(scenario)
        client = ROOT / "build/bin/vcmiclient"
        if not client.is_file():
            parser.error("图形客户端尚未编译，请按 README 的图形构建步骤生成 vcmiclient")
        bundle_client = client.parent / "Battle Simulator.app/Contents/MacOS/vcmiclient"
        if bundle_client.is_file():
            client = bundle_client
        subprocess.run([str(client), "--battle-scenario", str(scenario_path), "--nointro"],
                       cwd=client.parent, check=True)
        return
    if args.output is None:
        parser.error("批量模式需要 --output")
    args.output.mkdir(parents=True, exist_ok=True)
    results = args.input
    budget_audit = None
    scenario_bytes = None
    if args.scenario is not None:
        scenario_bytes = args.scenario.read_bytes()
        scenario = json.loads(scenario_bytes)
        if "point_buy" in scenario:
            budget_audit = audit(scenario)
        snapshot = (args.output / "scenario.json").resolve()
        snapshot.write_bytes(scenario_bytes)
        results = (args.output / "battles.jsonl").resolve()
        binary = args.binary.resolve()
        with (args.output / "run.log").open("w") as log:
            subprocess.run([str(binary), str(snapshot), str(results),
                            str(args.seed), str(args.count), str(args.rounds)],
                           cwd=binary.parent, stdout=log, stderr=log, check=True)
    with results.open() as stream:
        report = aggregate(json.loads(line) for line in stream if line.strip())
    report["results_sha256"] = hashlib.sha256(results.read_bytes()).hexdigest()
    if args.scenario is not None:
        report["scenario_sha256"] = hashlib.sha256(scenario_bytes).hexdigest()
    if budget_audit is not None:
        report["equal_budget_verified"] = True
        report["point_buy"] = budget_audit
    destination = args.output / "metrics.json"
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(destination.resolve())


if __name__ == "__main__":
    main()
