# 修仙战斗模拟器

2026-10-27 · Codex

依据 [GOALS.md](GOALS.md) 开发。战斗使用 VCMI C++ 服务器、原生六边形战场、回合队列和 BattleAI；没有另外实现一套简化战斗规则。

当前已可运行：手动窗口战斗、JSON 场景、英雄肉身、四宗各三门三级功法及本命神通、灵力与冷却、批量无界面对战、伤害日志、指标聚合及精确预算生成。修仙 mod 已包含境界压制、护法、领域、死亡士气惩罚与复活额度，规则见 [RULES.md](RULES.md)。**仍在开发中**：完整隐身与持续邪风领域、战后惩罚、AI 专项适配、平衡调参和跨机器确定性验收。

## 运行

打开游戏窗口并手动控制双方：

```sh
cd /Users/jin/Projects/battle_hero3
python3 simulate.py --play --scenario scenarios/demon-vs-talisman.json
```

这是双人热座模式：红蓝双方都由你操作，当前行动单位带黄色轮廓。点击可达地格移动，点击敌军攻击；`D` 防御、`W` 等待、`C` 打开法术书，选择法术后点击目标。`body-shock.json` 的红方体修拥有震地，蓝方起始灵力为零；蓝方先行动时可先按 `D`，轮到红方后施法。可以换成 `scenarios/sword-storm.json` 体验万剑归宗。手动模式不生成批量统计报告。

图形客户端复用现有英雄无敌 III 美术，修仙角色暂用原版头像和单位动画。启动时使用固定修仙模组；若本机已安装中文翻译和字体子模组，也会加载它们。不会修改你的模组预设。仅战斗模式保留场景指定灵力，不进行开局每日回蓝。

新增的 `demon-vs-talisman.json` 和 `sword-vs-body.json` 均为元婴肉身、三级宗门功法、150 灵力的手动演示场景。切换 `--scenario` 即可体验另一组。演示配置用于试技能，不标记为同预算平衡对局。

| 宗门 | 原版阵营外观 | 三门功法 | 本命神通 |
|---|---|---|---|
| 剑修 | 壁垒 | 剑遁诀、剑影诀、剑意诀 | 万剑归宗 |
| 体修 | 城堡 | 震地诀、护法诀、金刚诀 | 金身不灭 |
| 魔修 | 墓园 | 魔血诀、邪风诀、噬血诀 | 血炼尸傀 |
| 符修 | 塔楼 | 符兵诀、雷符诀、净符诀 | 七星符阵 |

阵营替代包含兵种、肉身动画、英雄头像与战场骑乘外观，战斗数值仍使用修仙配置，不继承原版兵种的全部特技。剑遁当前是原生瞬移加下一击必定暴击和免反击；邪风当前是周围三格友军的两回合加速。七星符阵为可见的七格持续火阵，敌我进入或在阵中行动均会受到伤害。

英雄肉身有常驻金色描边、金冠名牌和独立生命条；名牌显示宗门与境界，红蓝底色表示所属方。普通军队保留人数框，肉身使用的动画不与本宗普通兵种重复。幻象不会获得英雄名牌。

英雄法术只能在金冠肉身自己的行动回合释放；普通兵行动时法术书入口不可用。每轮仍限一次，施法后肉身还可移动或攻击；自动战斗遵守同一规则。重新启动游戏进程后使用新规则，已经打开的旧窗口不会热更新。

模拟日志的 `spells[].active_unit` 记录施法时正在行动的单位ID，可与 `units_initial` 的英雄肉身ID对应核验施法时机。

本机图形客户端已构建。需要重新构建时，在原有 CMake 构建目录执行：

```sh
brew install sdl2_image sdl2_mixer sdl2_ttf
cmake -S engine -B build -DENABLE_CLIENT=ON -DENABLE_SDL3=OFF -DENABLE_DISCORD=OFF
cmake --build build --target vcmiclient -j 8
```

下面是无界面的批量模式。

在项目根目录执行：

```sh
cd build/bin
./battle_sim ../../scenarios/hero-body-smoke.json ../../results.jsonl 42 10 100
```

参数依次为：场景文件、输出文件、起始种子、场数、最大回合数。后三项默认是 `1 1 100`。程序启动时只加载一次游戏数据，依次运行种子 `seed ... seed + count - 1`。输出路径会被覆盖；每场完成后写入一行 JSON 并刷新。

一条命令运行 1000 场并输出指标（在项目根目录）：

```sh
python3 simulate.py --scenario scenarios/cultivation-smoke.json --output results/cultivation --seed 1 --count 1000
```

结果目录包含输入快照 `scenario.json`、`battles.jsonl`、`run.log`、`metrics.json`。只聚合已有结果可使用 `python3 simulate.py --input results/cultivation/battles.jsonl --output results/recheck`。报告记录场景和结果的 SHA-256，按英雄类型分组；当前四种修仙英雄类型对应四个流派。只有运行前通过价格审计的场景才标记 `equal_budget_verified=true`；只聚合日志不继承未经核验的预算声明。

生成精确同预算场景：

```sh
python3 pointbuy.py --budget 5000 --schools sword body --realm Core --seed 42 --varied-loadout --output results/budget-5000.json
python3 simulate.py --scenario results/budget-5000.json --output results/budget-run --seed 1 --count 1000
```

`--realm` 支持 Qi、Foundation、Core、Soul、Deity；`--realms Qi Deity` 可分别指定双方境界，较高境界会占用更多预算、挤占军队资源。流派支持 sword、body、demon、talisman。军队随机分配，双方精确花完预算，最多七队且只有一个肉身。`--varied-loadout` 同时随机购买已计价的副技能、法宝和法术；省略时只随机军队。生成种子与战斗种子分开控制。无法精确花完的预算会报错，不会暗中少花。

兵种与肉身价格复用修仙 mod 的 `cost.gold`；其余价格位于 [config/point-buy.json](config/point-buy.json)，目前为调参初值，尚未平衡。预算文件保存价格指纹，配置改变后必须重新生成；主属性、灵力、副技能等级、法宝和神通均独立计价。主动功法授予的法术已计入副技能价格，不能绕过功法免费购买。随机军队仅使用本宗名册；符兵和尸傀不能直接购买。战争机器及目录外装备尚未计价，预算模式拒绝这些项目。

指标口径：只统计正常结束的对局，超时另列；胜率为获胜次数/出场次数，平局计入分母但不算获胜；伤害占比为累计英雄有效伤害/累计己方有效伤害，排除友伤与幻象。来源缺失时不输出伤害占比。存活率只统计存在肉身的样本。斩首胜率只统计有最终肉身死亡且首个死者由敌方击杀的对局；按最后一次致死包确定最终退场，成功重生后存活不算退场，同包双方死亡或缺少致死事件单列排除。报告保留逐场肉身结果，以及胜率的 Wilson 95% 区间；它们只描述当前固定场景和种子样本。

- `scenarios/native-smoke.json`：原版兵种对战，验证原生战斗链路。
- `scenarios/hero-body-smoke.json`：双方各一个英雄肉身，并可施放魔法神箭。原版骑士是肉身占位资源，还不是平衡后的修仙流派。
- `scenarios/cultivation-smoke.json`：剑修与体修肉身、修仙兵种对战，验证修仙 mod 与原生 BattleAI 的集成。
- `scenarios/sword-storm.json`：验证金丹剑修本命神通“万剑归宗”的全场伤害、灵力和冷却；实际AI会在冷却结束后再次施放。
- `scenarios/body-shock.json`：体修通过三级震地诀自动学习震地，验证范围控制与AI施法。体修另有金刚诀、护法诀，可通过 `secSkillLevel` 配置；等级、效果和价格见 [RULES.md](RULES.md)。

`status=completed` 表示原生服务器给出了结果；`round_limit` 表示回合或行动上限中止，此时没有 `winner`。胜方 `0/1` 分别对应双方场景槽，原生 `BattleSide::NONE=-1` 表示平局。`rounds` 是引擎已进入的回合编号，回合上限中止时可能刚进入下一回合。

结果还包括 `events`（AI 行动）、`units_initial` / `units_final`（单位数量、生命、格位、是否英雄肉身）、`spells`、`mana_remaining`。当前输出 `schema=3`，包含双方 `heroes` 类型及伤害事件的 `packet` 顺序。`damage_events` 逐次记录攻击、反击、法术及单位技能的来源、目标、回合、实际扣血和击杀数。英雄神通来源单位为 -1，仍记录所属方；肉身攻击与神通的 `hero_damage` 为 true。无法确认来源时 `source_side=-1`，不会猜测归给最近行动者。`reported_damage` 是原生包中的伤害值；`damage` 来自应用状态包前后的生命差。幻象目标单独标记 `target_clone`，统计时应排除；友伤也须单独处理。

初始快照在 BattleStart 数据包应用后立即取得，早于领域结算。现有记录尚不包含任意自定义脚本直接改写生命的完整审计；这类最终死亡没有致死包时会被报告为未知。预算审计仍未完成，统计器拒绝缺少必要字段的旧版日志。

## 场景

场景沿用 VCMI `BattleOnlyModeStartInfo`：`selectedTerrain` 和两个 `slots`。每方可配置 `selectedHero`、最多七个 `selectedArmy`、`primSkillLevel`、`secSkillLevel`、`artifacts`、`spells`、`spellBook`、`warMachines`。

新增字段：

- `commander`：肉身兵种标识，如 `core:champion`。每方至多一具，独立于七个军队槽。
- `mana`：战前灵力。省略或 `-1` 使用英雄法力上限，显式 `0` 保持零灵力。战后剩余值写入结果；连续战斗时应作为下一场输入，程序没有实现自动战役推进。

军队、主属性和副技能数组允许省略末尾空槽。当前命令行入口接受两位英雄的野战场景；原有图形界面的攻城场景生成仍保留。场景生成已抽取到 `engine/lib/StartInfo.cpp`，两种入口共享。

## 编译

源码位于 `engine/`，参考基线是本机 `/Users/jin/Projects/vcmi` 的 `ddb79cfdc1b1d66764cf1c61f02dd0031d86319f`，与 GOALS.md 内记录的上游版本不同。保留 VCMI 既有 CMake 和 gtest。当前机器复用已安装的 Conan 依赖：

```sh
cmake -S engine -B build -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_TOOLCHAIN_FILE=/Users/jin/Projects/vcmi/conan-generated/conan_toolchain.cmake \
  -DENABLE_CLIENT=OFF -DENABLE_LAUNCHER=OFF -DENABLE_EDITOR=OFF \
  -DENABLE_MMAI=OFF -DENABLE_NULLKILLER2_AI=OFF \
  -DENABLE_TEST=ON -DENABLE_PCH=ON -DENABLE_STRICT_COMPILATION=OFF
cmake --build build --target battle_sim vcmitest -j 8
```

另一台机器需要先按 VCMI 构建文档准备依赖，替换 toolchain 路径，并提供游戏数据。模拟器使用内存中的固定 `vcmi`、`cultivation` 模组预设，不读取或保存用户模组选择。资源仍沿用 VCMI 查找路径；内容哈希与跨机器结果比对尚未完成，不能据此承诺跨机器一致。

## 本地验证

```sh
python3 -m unittest discover -s tests -v
cd build/bin
./vcmitest '--gtest_filter=*Cultivation*:BattleOnlyScenario.*:HeroBodyBattleTest.*:BattleSpellCastTest.*'
```

功能测试实际运行 `battle_sim`，覆盖种子重复、正常结束、回合上限、错误输入、肉身与施法共存、零灵力不自动补满。gtest 覆盖共享场景生成、肉身死亡禁法和相关原生回归。验证记录见 `.codex/` 与 [verification.md](verification.md)。

本项目的引擎衍生代码遵循 [VCMI 许可证](engine/license.txt)。原版游戏数据沿用本机安装，没有复制到项目中。
