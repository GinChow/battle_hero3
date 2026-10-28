# 验证记录

## 2026-10-27 · Codex · 图形手动战斗

`python3 simulate.py --play --scenario scenarios/body-shock.json` 已实际弹出原生战斗窗口，双方为手动热座。中文与头像显示正常，场景灵力60/0保持不变；D防御和C打开震地法术书通过。相关原生142项、Python32项通过；扩大原生测试1069/1082通过，13项失败，详情在 `.codex/review-gui.md`。CUA鼠标事件坐标固定，鼠标施法尚未完成端到端验证；部分原版障碍图存在青色透明底。美术仍复用原版，完整GOALS未全部完成。

2026-10-26 · Codex

当前阶段已推进至修仙境界与规则层，完整目标尚未完成。

## 体修三门功法（2026-10-27 · Codex）

震地诀、金刚诀、护法诀三门三级功法均已配置并计价。unit-body-arts.log 的140项原生测试全部通过；functional-body-arts-final.log 的32项Python/实际进程测试全部通过。覆盖震地自动授予、范围/消耗/冷却/失能恢复，金刚领域防御与反击预估和服务器实伤一致、普通攻击无加成、离域/幻象失效，以及护法诀只保护肉身、三功法共同原生对战和累计计价。

为表达反击差异，在临时BattleAttackInfo及Lua伤害载荷增加isCounter，原生服务器和BattleAI的反击预估、附带目标均填充；不改变持久化布局。Lua文档由vcmiserver导出，日志lua-export-diamond.log。初次测试构建误用只读栈指针导致编译失败，改用BattleInfo::getStack取得可变测试对象；该次旧程序运行0测试不计入通过证据，之后编译及实际3组金刚测试通过。

完整目标仍未完成，尤其缺其他流派功法、战后结算、克制兵种与平衡。此前1000场报告是旧规则基线，不代表本轮技能后的胜率。

## 首个专属神通（2026-10-26）

万剑归宗已接入原生法术系统：金丹剑修解锁，全场敌军伤害，16灵力，3回合冷却；使用原生Bonus保存冷却，AI及服务器共用校验。unit-technique-final.log 的130项原生测试通过，包含服务器拒绝冷却中/错误流派/低境界/无肉身/灵力不足的请求，以及失败请求不启动冷却。functional-technique-final.log 的28项Python测试通过，包含真实BattleAI重复施法、回合间隔、灵力扣除、伤害来源及预算解锁校验。

构建记录build-technique-final.log。计价目录新增神通500点，价格指纹也纳入神通配置；旧预算文件须重新生成，示例budget-5000.json已更新。三门三级功法、其余神通和完整流派仍未实现，不能据此标记M2/M3完成。

## 指标与预算（2026-10-26）

`simulate.py` 已完成一次1000场真实原生运行并输出五类指标。`.codex/metrics-1000/metrics.json`：1000场全部completed、种子1–1000无缺失，平均9.385回合，英雄伤害1981121/2329421=85.05%，体修1000胜，剑修0胜；肉身存活率分别100%/0%，斩首方1000/1000获胜。来源未知伤害为0。这是固定阵容技术基线，equal_budget_verified=false，明显不能通过平衡要求。

`pointbuy.py` 已支持精确同预算、不同境界挤占军队预算、随机兵种与已计价技能/法宝/法术。`.codex/budget-smoke/metrics.json` 的10场样本审计双方各5000点：英雄伤害50.23%，体修全胜，斩首方全胜；不是平衡通过证据。输入场景为 scenarios/budget-5000.json。

tests-budget-metrics-final.log 中25项测试通过，含CLI完整链路；随后新增不同境界预算测试，unit-pointbuy-final.log 的8项预算测试通过，总计26个测试用例均有通过证据。build-metrics-final.log 构建成功。现有技能计价不代表专属三门功法已实现；专属技能、克制兵种、AI及平衡仍缺。

- CMake 已成功构建 `battle_sim` 与 `vcmitest`，日志 `.codex/build-commanders-final.log`。
- 25 项 gtest 通过，覆盖场景生成、肉身配置与死亡禁法、原生施法及英雄等级/技能相关行为，日志 `.codex/unit-commanders.log`。
- 6 项真实可执行程序功能测试通过，日志 `.codex/functional.log`。
- 原生场景种子 42–44 重复运行，结果和行动记录一致；不代表跨机器验证，也不代表全部规则已实现。
- 英雄肉身场景种子 42–44 均完成，双方各一具肉身、英雄施法发生、灵力消耗正常；输出 `.codex/hero-body.jsonl`。
- 1000 场占位肉身基线全部正常结束，种子完整覆盖 1–1000：左方 879 胜、右方 121 胜，平均 6.227 回合，最长 18 回合。完整结果 `.codex/native-1000.jsonl`，进度 `.codex/native-1000.log`，摘要 `.codex/native-baseline.json`。该数据不作为修仙流派平衡达标证据。

新增验证：`build-domain-distance.log` 构建成功；`unit-domain-distance.log` 中 48 项原生测试全部通过，含境界公式、护法、领域死亡/抵消/压制、重生与士气先后、复活额度不可重复使用、24 组奇偶行六方向领域边界。`functional-cultivation.log` 中 7 项真实程序测试通过，包括修仙场景种子 42–44 重复运行。Lua API 文档已由 vcmiserver 自动导出，见 `lua-export-distance.log`；引擎 diff 格式检查通过，参考仓库工作区无修改。

复活口径补充验证：`build-resurrection-budget.log` 构建成功，`unit-resurrection-budget.log` 中 52 项原生测试通过。4、9、10 名战前士兵分别获得 0、1、2 人额度，三种战争机器实际在场且不增额度；召唤、幻象及重复初始化不增额度；零额度仍可治疗残血而不复活。`functional-resurrection-budget.log` 中 7 项真实程序测试通过。

伤害日志验证：`unit-damage-events-final.log` 中 124 项测试通过，覆盖修仙规则、原生伤害计算、火盾、毁灭和法术。`functional-damage-events-final.log` 中 8 项真实程序测试通过，新增逐事件来源、反击归因和总生命损失守恒；英雄神通来源通过原生伤害包显式传递。schema 2 输出实际扣血和击杀。`damage-smoke.jsonl` 保存 10 场修仙场景样本。Lua API 已自动重新导出。

扩大回归曾有 8 项原生伤害测试失败：修仙 mod 的 patches 数组替换了原生列表，丢失伤害上限、减攻等规则。改用 JsonUtils 支持的 appendItems 后，124 项全部通过。失败日志保留为 unit-damage-events.log，不能作为最终通过记录。

已有当前目录范围的预算一致性证据，但没有目标胜率达标证据；任意自定义状态改写的伤害审计、专属功法及其计价、完整流派、战后惩罚和尸傀边界尚未完成。未运行图形界面、联网、其他操作系统。完整验收必须继续按 GOALS.md 推进。1000场使用当前统计器重新聚合，与原报告的全部统计字段及结果哈希一致（metrics-1000-recheck）。

发现并修复：仅战斗 JSON 读取曾要求填满兵种/技能数组，短数组触发 `vector` 越界；共享地图生成回调需在使用前绑定新地图；复杂 JsonNode 的 `toCompactString()` 仍带换行，输出时已去除排版换行使其成为有效 JSONL。编译修复包括缺失 MapFormat 头文件、通过官方 AI 工厂访问非导出 BattleAI、通过公共接口读取单位槽位与兵种。


## 2026-10-27 · Codex：宗门技能、阵营替代与英雄视觉辨识

已完成本轮代码与本地验证，详见 `.codex/review-sects.md`。工具：functions/exec_command读取原生Lua/C++/JSON、rg检索；apply_patch添加功法脚本和原生gTest、修改预算与客户端Canvas；Python转换配置并生成两组场景；CMake构建；CUA核对原生窗口和法术书及金冠名牌。无sequential-thinking/shrimp/code-index可用，降级记录见sects-plan.md/context-sects.json。

184项相关原生测试、34项Python测试通过；两组共20场自动对战完成。英雄视觉追加修改后客户端构建通过，并在保留旧局的情况下另开窗口确认金色描边、红蓝金冠名牌与独立生命条。完整输出：sects-native-final.log、sects-python-final.log、hero-marker-python.log、build-hero-marker.log、sects-smoke-demon/、sects-smoke-sword/。早期失败及修复原因见review-sects.md，不把失败尝试当作通过。

当前适配：剑遁＝瞬移/下一击暴击免反击；邪风＝施放时周围三格友军加速两回合。完整隐身、持续邪风领域、平衡、战后规则仍未完成。旧的全量VCMI测试失败和青色障碍贴图问题未声称解决。


2026-10-27 · Codex：英雄施法窗口限制为己方真实肉身的行动回合。共享查询同时覆盖GUI、服务器与BattleAI；保留每轮一次施法及施法后肉身行动，被动效果不受限制。构建build-body-turn.log成功，198项相关原生测试body-turn-native.log及35项Python测试body-turn-python.log通过；新增AI真实对局逐条核对spells[].active_unit。完整方案与审查见body-turn-plan.md/review-body-turn.md。现有游戏进程保留，需退出重启加载新逻辑。工具调用为本地rg/exec_command/apply_patch/CMake/gtest/unittest，无远程操作。
