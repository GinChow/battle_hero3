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


## 2026-10-29 · Codex：五首战斗背景音乐替换

- 将 audio_assets 的五首 MP3 按 README 映射复制至修仙模组 Content/Music/COMBAT01.MP3～COMBAT05.MP3；覆盖四个原版资源标识，新增第五个。
- 复用 CMusicHandler 的随机选曲逻辑，不改引擎代码；随机允许连续重复。
- 验证：五首逐一 SHA-256 一致、ffmpeg 完整解码通过；实际图形战斗启动成功，运行日志恰好发现五个 MUSIC/COMBAT 资源，并实际加载模组 COMBAT03 播放。
- 已结束本次测试启动的客户端。原有 music/Dungeon 缺失警告仍存在，与本次战斗音乐替换无关。
- 证据：.codex/music-verification.json、.codex/music-runtime.log、.codex/music-client-smoke.log。


## 2026-10-30 · Codex：替换八首战斗开场音乐

将 audio_assets/battle_intro_new 中八首 MP3 转换为修仙模组 Content/Sounds/BATTLE00.wav～BATTLE07.wav。复用现有随机播放，不改引擎，保留完整时长。README 记录映射。

验证：八首均为 48 kHz 双声道 PCM 16-bit，转换前后解码采样完全一致；实际客户端随机加载模组 BATTLE03.wav，随后成功播放 COMBAT 战斗音乐。证据：.codex/intro-new-verification.json、.codex/intro-new-runtime.log。


## 2026-10-31 · Codex：战斗 BGM 同曲循环

修改 SDL2/SDL3 MusicEntry::play：battle 集合仅首次播放随机选曲，后续复用当前音乐；保留集合标识，其他集合播放策略不变。README 已更新。

验证：cmake --build build --target vcmiclient -j 8 成功；git diff --check 通过。实际图形战斗完整播放 COMBAT04（破阵令）后再次播放 COMBAT04，日志仅一次 Loading music、两次 Playing music，验证自然结束回调复用原曲而未重选。测试客户端已关闭。本机只编译/运行 SDL2；SDL3 修改经对照审查，未构建。链接有原有 macOS SDK 版本警告。

证据：.codex/build-bgm-loop.log、.codex/bgm-loop-runtime.log、.codex/bgm-loop-client.log、.codex/context-bgm-loop.json。

## 2026-11-01 · Codex：水墨武侠四兵种替换

从水墨武侠 Character 选用 C012、C013、C018、C005，分别接入剑修御剑弟子、体修筑基护法、魔修筑基护法、符修金丹护卫。包含 290 张透明动作帧、8 张头像和 4 个 VCMI 动画 JSON；只修改这四个兵种的 graphics 字段。D51 的 272 个 JSON 中没有同时包含 run 与 death 的角色，本批未选用。

- 本地 `python3 -m unittest discover -s tests -v`：36 项通过，含原生模拟器功能回归和新增资源引用/动作组/PNG 尺寸检查。
- 全部动作帧非空、透明 RGBA，内容未碰到画布边界；死亡组以倒地动作衔接静态 dead，尸体组引用相同末帧。
- 实际 SDL2 客户端加载四种角色，核对双方镜像、队列头像、选中描边、移动后站位与倒地尸体。日志没有新增角色资源缺失或空动画错误。
- 所有非 graphics 字段与变更前完全一致；根项目及 engine 的 `git diff --check` 通过。没有引擎代码变化，无需编译。

范围限制：横版素材共用上下攻击，防御复用受击，转身通过原生镜像；其他兵种、英雄和音效仍使用原资源。预览中还观察到障碍物的青色背景和既有 Dungeon 音乐缺失提示，不涉及本次四套人物资源，未在此任务内处理。

证据：`.codex/wuxia-inventory.json`、`.codex/wuxia-export.json`、`.codex/wuxia-actions.png`、`.codex/wuxia-tests.log`、`.codex/wuxia-client-bundle.log`；可复查的来源及哈希保存在 `engine/Mods/cultivation/wuxia-art.json`。

四兵种预览场景功能冒烟：`battle_sim ... 42 3 100` 的种子42、43、44全部 completed，见 `.codex/wuxia-battles.jsonl`。


## 2026-11-01 · Codex：武侠动画首次播放卡顿

根因：动画帧在首次绘制时懒加载，上一版每组开启 generateShadow=2 和 generateOverlay=1，导致绘制路径同步生成阴影、模糊和描边。缓存后不再计算，与首次卡顿现象一致。已用引擎原有 CSDL_Ext 函数离线生成290帧的580张配套图层，移除实时生成选项，沿用原生 -SHADOW/-OVERLAY 加载约定。人物原帧、动作映射和属性不变，无需编译。

本机微基准（原引擎函数，clang++ -O2，290帧）：原PNG加载+阴影/描边生成平均450.365ms，P95 533.647ms；读取预生成三层平均1.353ms，P95 1.501ms。仅测图层准备，不含完整游戏帧时间、缩放或磁盘冷缓存；不能当作整场战斗FPS提升倍数。日志：.codex/wuxia-layer-benchmark.log。

验证：580张图层全部可解码、非空且为450×400 RGBA；复用原函数保证阴影和描边语义一致，合成图片已目视检查；test_wuxia_assets.py通过，检查所有动画引用、头像、图层及关闭实时生成。git diff --check通过。未关闭用户正在操作的旧窗口，本轮未重新启动GUI测量帧率；需重启客户端加载新配置。


## 2026-11-01 · Codex：四兵种30 FPS重采样

完成：从原始Spine重新采样870张动作帧，替换原290张。动态动作帧数×3；新增graphics.animationTime.frameRate=30，idle=30；引擎默认frameRate=10，未配置的其他兵种保持原速度。移动距离计算不变，单帧转身仍用原10FPS×战斗倍率。stand/run按[0,duration)采样，移除重复终点。1740张阴影和描边继续离线生成。

验证：
- 新旧动作帧数/帧率比一致，待机与跑步首尾像素不同；所有人物帧非空且未触及450×400画布边界。
- 实际姿势数增加，例如C012攻击14→42、跑步8→27；不是重复旧帧。
- 全部1740配套图层可解码、非空、RGBA；头像8张保留。
- cmake --build build --target vcmiclient battle_sim vcmitest -j 8成功；有既有SDK/链接路径警告。
- 117项相关gtest通过，36项Python单元/功能测试通过，包含动作时长契约和原生战斗回归。
- 新构建SDL2客户端已进入预览场景，四个角色、双向镜像和图层正常可见；未测量实际显示FPS，不据截图声称整场性能指标。检测到用户操作后停止额外UI点击，保留预览窗口。
- 所有非graphics兵种字段与原始配置完全一致；git diff --check通过。

证据：.codex/context-wuxia-30fps.json、wuxia-30fps-characters.json、wuxia-30fps-build-final.log、wuxia-30fps-gtest.log、wuxia-30fps-python-tests.log、wuxia-30fps-client.log。上一版资源副本：.codex/wuxia-10fps-backup/。临时导出/安装脚本：render-wuxia-30fps.mjs、bake-wuxia-30fps.py、install-wuxia-30fps.py。来源和时长基线写入engine/Mods/cultivation/wuxia-art.json。


## 2026-11-01 · Codex：15FPS试用配置

按用户确认将四兵种从30FPS降为15FPS，同步降采样图片。循环隔帧取样；非循环均匀取样并保留末帧；动作时长与基准偏差不超过1/30秒，移动与转身速度不变。预生成阴影和描边全部保留。当前441人物帧、882配套图层、8头像、4JSON，总计8983206字节（约8.57MiB）。上一版完整备份在.codex/wuxia-30fps-backup。

验证：资源契约单元测试通过，全部PNG解码并检查非空，git diff --check通过。没有引擎变化，无需重编译；当前打开的客户端需重启以加载新资源，未操作用户窗口。执行脚本.codex/set-wuxia-15fps.py；记录包含动画时长量化容差检查。结论：通过。


## 2026-11-01 · Codex：新增四兵种外观与四宗英雄全显示替换

新增普通兵种：C021→swordDisciple，C011→goldGuard，C020→demonElder，C003→talismanElder。英雄：Z001→剑修、C026→体修、Z003→魔修、Z002→符修，覆盖各五境界肉身共20条配置，以及大小头像与战场两侧形象。所有新资源15FPS。当前总计8普通兵种外观、4宗英雄、1483张人物/侧边帧、总资源26818176字节（约25.58MiB）。未引用导出帧已从运行资源剔除；源素材未改动。

英雄使用原生battleImage，新增可选battleAnimationFrameRate（默认10，本次15）；旗帜仍10FPS。getFrame返回原10FPS法术释放时间线，因此释放时刻仍0.4秒，侧边施法12帧/15FPS=0.8秒。新增字段仅图形配置，不改变兵种/英雄战斗数据。C021/C011的skill01包含隐身空白，改用可见的skill02；实际格挡动作可用时采用block。

验证：
- 本批原始导出1170帧（含侧边）；经去除未引用帧后与已有资源合计1483帧。全部导出及图层解码、非空、边界验证通过。
- 构建vcmiclient、battle_sim、vcmitest成功；有既有SDK与链接路径警告。
- 118项相关gtest、37项Python测试通过，新增英雄五动作组、头像、20肉身关联、施法时长契约检查。
- 魔修/符修扩展预览种子42/43/44三场原生模拟全部completed。
- SDL2实际画面确认剑修/体修头像、两侧形象、金冠肉身及新增四兵种；金冠名牌、阴影与描边正常。魔修/符修图层离线合成及资源契约已检查，未声称实际GUI帧率测量。
- 所有非graphics兵种字段、非图形英雄字段与更换前逐项一致。两个仓库git diff --check通过。

证据：.codex/context-wuxia-expansion.json、wuxia-expansion-selection.png、wuxia-heroes-phases.png、wuxia-expansion-build-final.log、wuxia-expansion-gtest.log、wuxia-expansion-python-tests.log、wuxia-expansion-client-sword.log、wuxia-expanded-battles.jsonl。来源哈希与映射：engine/Mods/cultivation/wuxia-art.json。预览：scenarios/wuxia-art-preview.json及wuxia-heroes-preview.json。

已知非本任务问题：原障碍物青色背景、Dungeon音乐缺失提示仍存在。首次功能冒烟从项目根目录运行时路径失败，改为既有build/bin工作目录后通过。临时导出脚本插入位置在运行前检查发现并修正；透明技能动作经实际帧检查后替换，无空白帧进入交付。

2026-11-01 · Codex：移除角色金色描边并加入当前行动脚下青蓝光环。使用资源库既有20帧动画、15 FPS，增强版112×62画布、透明度3.2倍并上移12像素。CMake vcmiclient构建成功；全量38项Python测试通过，增强后3项资源测试再次通过；git diff --check通过。实机截图确认无金边、行动切换后光环改变角色，增强版光环明显可见。构建仍有原有库路径/macOS部署目标链接警告。移动跟随与死亡隐藏已按动画位置及alive状态实现；未单独测量帧耗时、未实机覆盖死亡。既有青色障碍物背景不属于本次修改。

2026-11-01 · Codex：开场卡顿调查。光环预载实测16ms，采样定位到SDLImageOptimizer::optimizeSurface逐像素SDL_GetRGBA。使用SDL alpha掩码替代不必要的完整颜色解码。8种像素格式524288组合与SDL参考一致，56张实际PNG裁切边界一致，独立扫描139.608→4.968ms。GUI后测光环预载9ms，角色≥10ms加载从384条降至1条（不同运行时长，只作辅助证据）。仅修改SDL2实际使用路径，SDL3后端未改动；图像美术无变化。临时CAnimation与marker计时日志已移除。工具：exec_command运行rg/sample/CMake/SDL测试；apply_patch修改优化器；日志见marker-*-client.log、marker-startup-sample.txt、alpha-mask-validation.log。

## 2026-11-01 · Codex：战斗场景验证

- 武侠资源测试：3项通过。
- 7种背景引用及PNG完整解码、800×556尺寸检查通过；所有现有场景地形覆盖。
- 实际客户端加载成功，新背景可见；障碍物青色矩形底异常另行记录，未归因于本次修改。
- 根仓库与engine的 git diff --check 通过。
- 原生战斗回归输出：
```text
............
----------------------------------------------------------------------
Ran 12 tests in 14.199s

OK

```

## 2026-11-01 · Codex：障碍物替换验证

- 沙地四种障碍完整覆盖；动画路径可解析，RGBA透明边缘验证通过。
- 仅覆盖animation字段，原占格参数未修改。
- 实机预览：原青色底块已消失，碎石透出地面。
- 武侠资源测试：3项通过；git diff --check通过。
- 原生回归：
```text
............
----------------------------------------------------------------------
Ran 12 tests in 13.691s

OK
```
- 范围：只替换沙地使用的四种障碍，其他原版障碍未作全面透明色验证。

## 2026-11-01 · Codex：四张生成地图

原图保存、基础/2倍纹理适配、九背景graphics引用检查通过。最终保持原地形池与随机过程，38项本地测试全部通过。先前扩大背景池导致冷却样本断言失败，已撤回该方案。2倍纹理需启用高清纹理并由引擎请求2倍资源；不声称已验证所有显示倍率。

```text
......................................
----------------------------------------------------------------------
Ran 38 tests in 16.746s

OK
```


## 2026-11-02 · Codex：移除战斗开场音效

删除 BattleInterface 开场音效播放与完成回调，直接解锁战斗并播放原有背景音乐。CMake vcmiclient 构建通过，38 项既有 Python 测试通过，engine git diff --check 通过。日志：`.codex/remove-battle-intro-build.log`、`.codex/remove-battle-intro-tests.log`。保留既有链接环境警告；未进行实际听音验证。
