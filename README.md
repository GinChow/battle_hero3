# 修仙战斗模拟器

2026-10-27 · Codex

依据 [GOALS.md](GOALS.md) 开发。战斗使用 VCMI C++ 服务器、原生六边形战场、回合队列和 BattleAI；没有另外实现一套简化战斗规则。

当前已可运行：手动窗口战斗、JSON 场景、英雄肉身、四宗各三门三级功法及本命神通、灵力与冷却、批量无界面对战、伤害日志、指标聚合及精确预算生成。修仙 mod 已包含境界压制、护法、领域、死亡士气惩罚与复活额度，规则见 [RULES.md](RULES.md)。**仍在开发中**：完整隐身与持续邪风领域、战后惩罚、AI 专项适配、平衡调参和跨机器确定性验收。

## 运行

### 行动范围颜色（2026-11-03 · Codex）

当前行动角色的范围使用深蓝青色填充（#286a9b，46%不透明度），逐格蓝色描边为1.5逻辑像素，并使用透明留边避免外围边线被裁细；鼠标悬停战场角色或队列头像时，预览范围使用朱红色填充与浅红色内侧虚线。按用户反馈撤回整片外轮廓方案，恢复逐格显示。1×/2×/3×素材同步更新，正在运行的模拟器需重启加载。

### 其余战斗窗口统一为 Y700 水墨 UI（2026-11-03 · Codex）

设置（常规、冒险地图、战斗及子设置）、大小功法簿、快捷功法配置、单位详情、提示/确认弹窗、撤退/投降确认与战斗结算已接入 Y700 原始购买素材。面板、边框、按钮、勾选框、滑块、翻页和属性图标沿用同一套黑墨/飞白风格；12 项功法的书内图标与快捷栏使用相同 U0088 美术。中文/英文菜单文字由原生控件绘制，保留至尊/古宋字体、点击尺寸与回调。

原生导出器仍为 `art_assets/battle-ui-v3/install.cjs`，新增资源具备 1×/2×/3×版本。结算用 Y700 胜负图案替换旧影片；水墨功法簿直接翻页，避免旧羊皮纸翻页影片闪现。修复共享弹窗边框在窄角片下末段越界。已经构建本地客户端，重新启动模拟器后加载。

55 项本地测试通过，包含17项UI测试。设置战斗页已实际显示水墨样式；后续桌面自动化连续超时，其他窗口尚未完成逐项实机点击验收。范围与验证记录见 `specs/cultivation-battle-ui-v3/window-extension.md` 和 `.codex/review-y700-windows.md`。`art_assets/battle-ui-v3/window-assets-preview.png` 是导出底板/控件预览，不是游戏截图。

### 高清与文字可读性修复（2026-11-03 · Codex）

macOS SDL2 窗口现已启用 Retina 输出。12 套武侠角色共 1,483 张在用动作帧从原 Spine 3.6 重绘为 3×资源，并生成 2×版本、高清头像及预生成图层；逻辑尺寸、锚点、动作帧序和15FPS时序不变。资源分别位于 `Content/Sprites2x/cultivation/wuxia` 与 `Content/Sprites3x/cultivation/wuxia`，记录见 `engine/Mods/cultivation/wuxia-art.json` 的 `highResolution`。

按用户要求，原生界面恢复至尊书法体与古宋体：标题、按钮及功法名称使用至尊，正文和数字使用古宋。按钮标签从13增大至18逻辑字号；保留高清修复后的正文尺寸、人数框、血量名牌和英雄属性行距，名牌绘制在角色之后。当前原生适配器为 `art_assets/battle-ui-v3/install.cjs`，其中82项UI资源提供3×版本，其余沿用已有1×/2×资源。战场背景仍受原始约1500像素图片的细节上限约束。

本机视频设置已启用 `xbrz3` 和高清纹理；实测输出3456×2104，日志确认读取3×角色与33像素的小字字体。设置备份在 `.codex/settings-before-hd-2026-11-03.json`。其他机器可在视频选项选择3×缩放滤镜并开启高清纹理。高清修复的49项本地测试、客户端编译通过；恢复字体后11项资源测试与九个按钮的多密度文字边界检查通过。高清修复记录见 `.codex/review-hd-2026-11-03.md`。

### 古卷兵阵 · 水墨战斗 UI（2026-11-02 · Codex）

修仙模组已接入批准的水墨 SVG 组件：宣纸面板、墨色文字、朱砂防御印、功法签、古刻象形图标、队列与阵营名牌。撤退使用奔走离场图案，投降使用白旗；12 门自定义法术使用对应的新图标。沙地改用水墨战场。底部“防御”仍执行原生防御动作，原有快捷键保留。窗口逻辑高度达到 720 时，12 个快捷法术槽移到底部横排；较小窗口沿用侧栏。战场位置与独立拾取遮罩保持原生几何，实际布局是设计稿的原生适配版。人物、头像、法术书内页、设置及确认弹窗仍采用现有资源。

直接查看：

```sh
python3 simulate.py --play --scenario scenarios/wuxia-art-preview.json
```

测试有法术的场景可使用 `scenarios/sword-storm.json`。新的客户端已完成本地编译；运行中的旧窗口需要重新启动才能加载。资源位于 `engine/Mods/cultivation/Content/`，源文件及原生适配导出器位于 `art_assets/battle-ui-v2/`，运行素材清单为 `engine/Mods/cultivation/battle-ui-art.json`。提供 91 项原生素材的 1×/2×版本。不修改共享游戏安装目录。

本地 46 项测试与客户端编译通过，已启动游戏检查水墨渲染。自动桌面输入工具在客户端更新后持续报告状态变化，实机点击操作未完成自动验证；详见 `verification.md`。

### 战斗场景（2026-11-01 · Codex）

战斗背景现使用四张生成地图：仙山演武场、竹林秘境、古关战场、雪域古境。高清原图保存在 [`art_assets/battlefields/`](art_assets/battlefields/)，模组内提供 800×556 基础纹理与 1600×1112 的 `Data2x` 纹理；后者在启用高清纹理且引擎使用2倍资源时加载。尺寸适配直接取自原图，不从800像素版本放大。

沿用原生地形与背景池：沙地显示古关战场，泥地与草地显示仙山演武场或竹林秘境，雪地显示雪域古境。只覆盖九个原生背景的 `graphics`，保持固定种子的随机过程、地形属性、站位与阻挡规则。现有沙地演示直接显示新古关背景；场景的 `selectedTerrain` 为 `core:snow` 时显示雪域。原图尺寸、哈希及运行文件见 [场景素材清单](engine/Mods/cultivation/battlefield-art.json)。退出旧客户端并重新启动即可生效，无需编译。旧幽林图片不再被战场配置引用。

2026-11-01 · Codex：沙地演示的四种随机障碍物已替换为资源库 Monster 中的透明碎石堆（`minotaur_spine/ef_rock_summon.png`）。使用 RGBA PNG 按原阻挡格布置，保留原占格、落点规则和随机选择逻辑；实机确认原障碍物的青色矩形底已消失。来源与四种布局见 [障碍物素材清单](engine/Mods/cultivation/obstacle-art.json)。这项替换仅覆盖沙地使用的四种障碍物，其他障碍物仍使用原素材；没有修改引擎的透明色处理。

### 战斗背景音乐

2026-10-29 · Codex

修仙模组使用 `audio_assets/` 提供的五首音乐。运行资源位于 `engine/Mods/cultivation/Content/Music/`，通过同名资源覆盖原版四首战斗音乐，并增加第五首；不修改共享 VCMI 安装目录。每场战斗开始时从五首中随机选择一首，随后循环播放同一首，直到战斗结束（2026-10-31 · Codex）。

| 原始音乐 | 模组运行文件 |
|---|---|
| `audio_assets/battle1.mp3` | `COMBAT01.MP3` |
| `audio_assets/东方奇幻.mp3` | `COMBAT02.MP3` |
| `audio_assets/幻想史诗.mp3` | `COMBAT03.MP3` |
| `audio_assets/破阵令.mp3` | `COMBAT04.MP3` |
| `audio_assets/雨夜潜行.mp3` | `COMBAT05.MP3` |

运行文件是原始音乐的副本；以后替换音乐时需同步更新对应运行文件，并重启客户端，无需编译。菜单与胜负结算音乐保持原有配置。

战斗开场音乐（2026-10-30 · Codex）使用 `audio_assets/battle_intro_new/` 的八首 MP3，保留完整音频并转换为 48 kHz、双声道、16-bit PCM WAV，放在 `engine/Mods/cultivation/Content/Sounds/`。每次开战随机播放一首，结束后进入战斗背景音乐；无需修改引擎或原版 SND 资源包。

| 新开场音乐 | 模组运行文件 |
|---|---|
| `云海交锋.mp3` | `BATTLE00.wav` |
| `出鞘迎敌.mp3` | `BATTLE01.wav` |
| `幽杀突现.mp3` | `BATTLE02.wav` |
| `御剑列阵.mp3` | `BATTLE03.wav` |
| `御剑迎战.mp3` | `BATTLE04.wav` |
| `拔剑迎敌.mp3` | `BATTLE05.wav` |
| `法阵初成.mp3` | `BATTLE06.wav` |
| `魔气爆发.mp3` | `BATTLE07.wav` |

更换源 MP3 后需重新转换对应 WAV 并重启客户端。原始开场音效的解包副本保留在 `audio_assets/battle_intro_original/`。

打开游戏窗口并手动控制双方：

```sh
cd /Users/jin/Projects/battle_hero3
python3 simulate.py --play --scenario scenarios/demon-vs-talisman.json
```

这是双人热座模式：红蓝双方都由你操作，当前行动单位脚下显示青蓝色循环光环。点击可达地格移动，点击敌军攻击；`D` 防御、`W` 等待、`C` 打开法术书，选择法术后点击目标。`body-shock.json` 的红方体修拥有震地，蓝方起始灵力为零；蓝方先行动时可先按 `D`，轮到红方后施法。可以换成 `scenarios/sword-storm.json` 体验万剑归宗。手动模式不生成批量统计报告。

图形客户端以英雄无敌 III 美术为基础，已有八个普通兵种及四宗英雄换成水墨武侠角色。英雄替换覆盖五个境界的金冠肉身、大小头像和战场两侧形象；其他普通兵种仍使用原版外观。启动时使用固定修仙模组；若本机已安装中文翻译和字体子模组，也会加载它们。不会修改你的模组预设。仅战斗模式保留场景指定灵力，不进行开局每日回蓝。

### 水墨武侠兵种（2026-11-01 · Codex）

从 `assets_browser/roots.json` 指向的水墨武侠 `影之刃3/Character` 中选用四套角色，已替换战场动画及大小头像：

| 兵种 | 素材 | 外形 |
|---|---|---|
| 剑修御剑弟子 `swordSwordGuard` | C012 | 斗笠剑客 |
| 体修筑基护法 `guardian` | C013 | 持棍武僧 |
| 魔修筑基护法 `demonGuardian` | C018 | 红发双刃 |
| 符修金丹护卫 `talismanGoldGuard` | C005 | 蓝衣术士 |

后续追加四个普通兵种外观：

| 兵种 | 素材 | 外形 |
|---|---|---|
| 剑修炼气弟子 `swordDisciple` | C021 | 白衣双刃武者 |
| 体修金丹护卫 `goldGuard` | C011 | 金甲剑客 |
| 魔修元婴长老 `demonElder` | C020 | 金甲异人 |
| 符修元婴长老 `talismanElder` | C003 | 蓝衣御刃者 |

四宗英雄使用独立形象，各自五个境界共用该宗形象，金冠、生命条和境界名牌保留：

| 英雄 | 素材 | 外形 |
|---|---|---|
| 剑修 | Z001 | 红黑剑客 |
| 体修 | C026 | 重甲武者 |
| 魔修 | Z003 | 紫袍术士 |
| 符修 | Z002 | 紫衣修士 |

英雄大小头像、金冠肉身和两侧施法形象保持一致。侧边英雄通过原生 `battleImage` 单独覆盖；`battleAnimationFrameRate` 为15，原版英雄默认10。旗帜仍按原速播放，法术释放时刻保持0.4秒，新施法动作全长0.8秒。具备 `block` 的新增角色使用原始格挡动作；C021和C011含隐身空白帧的 `skill01` 未用于战斗，改用完整可见的 `skill02`。所有更换只涉及美术及动画时序，不新增兵种数值或改动现有战斗规则。

包含待机、移动、受击、攻击、技能、倒地和尸体姿势。原素材的 `dead` 主要是尸体定格，死亡动画依次使用 `atked_fall`、`atked_fall_end`、`dead`。上下方向攻击共用横版攻击动画，左右朝向由 VCMI 镜像；防御复用受击动作，复活使用引擎默认的死亡倒放。战斗数值、技能和原有音效保持原配置。

资源通过 VCMI 原生 PNG 序列与动画 JSON 加载，无需修改或重新编译引擎，也无需运行时安装 Spine。运行资源位于 `engine/Mods/cultivation/Content/Sprites/cultivation/wuxia/`，来源、动作与导出参数见 [素材清单](engine/Mods/cultivation/wuxia-art.json)。已同时检查 D51 的 272 套源文件，其中没有同时具备移动和死亡动作的角色，因此本批未选用 D51。

重启游戏后，原有两组宗门演示会直接显示对应替换。集中查看四个新兵种的双方朝向：

```sh
python3 simulate.py --play --scenario scenarios/wuxia-art-preview.json
```

此场景用于外观检查，不是平衡测试场景。

`wuxia-art-preview.json` 查看剑修、体修英雄与新增兵种；`wuxia-heroes-preview.json` 查看魔修、符修英雄。原有 `sword-vs-body.json` 和 `demon-vs-talisman.json` 也会直接显示新外观。

2026-11-01 · Codex：人物的阴影与选中描边已离线生成，分别保存在同名 `-SHADOW.png` 和 `-OVERLAY.png` 中。动画配置不再要求引擎在首次绘制每帧时实时生成这两层，避免首次播放新动作时的同步计算卡顿。人物帧、动作、阴影样式和描边样式保持一致；更新后需要退出旧客户端并重新启动。

首批四个角色先从原始 Spine 重采样到 30 FPS，再按试用要求降采样为 **15 FPS**，该批保留441张人物动作帧和882张预生成图层；本次追加角色也使用15FPS。循环不重复终点，非循环保留动作末帧；首批动作时长量化误差最多约33毫秒。`graphics.animationTime.frameRate` 控制动作基础帧率，仍受战斗速度倍率影响；`idle` 独立设为15。未指定 `frameRate` 的其他兵种保持原来的10FPS基准，移动距离和转身速度不变。本次英雄侧边动画包含时序支持，需使用本机已更新构建的客户端。

新增的 `demon-vs-talisman.json` 和 `sword-vs-body.json` 均为元婴肉身、三级宗门功法、150 灵力的手动演示场景。切换 `--scenario` 即可体验另一组。演示配置用于试技能，不标记为同预算平衡对局。

| 宗门 | 原版阵营外观 | 三门功法 | 本命神通 |
|---|---|---|---|
| 剑修 | 壁垒 | 剑遁诀、剑影诀、剑意诀 | 万剑归宗 |
| 体修 | 城堡 | 震地诀、护法诀、金刚诀 | 金身不灭 |
| 魔修 | 墓园 | 魔血诀、邪风诀、噬血诀 | 血炼尸傀 |
| 符修 | 塔楼 | 符兵诀、雷符诀、净符诀 | 七星符阵 |

阵营替代包含兵种、肉身动画、英雄头像与战场骑乘外观，战斗数值仍使用修仙配置，不继承原版兵种的全部特技。剑遁当前是原生瞬移加下一击必定暴击和免反击；邪风当前是周围三格友军的两回合加速。七星符阵为可见的七格持续火阵，敌我进入或在阵中行动均会受到伤害。

英雄肉身保留金冠名牌和独立生命条，取消角色金色描边；名牌显示宗门与境界，红蓝底色表示所属方。普通军队保留人数框，肉身使用的动画不与本宗普通兵种重复。幻象不会获得英雄名牌。

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

当前行动光环取自资源库 `FX_Common_Aura_StatusDelta_Target`，使用20帧透明图片，以15 FPS循环播放，随行动角色切换并跟随移动。资源来源和加工参数见 `engine/Mods/cultivation/active-unit-art.json`。

2026-11-02 · Codex：四种战场已按约15%远景/85%可站立地面重新生成，保留石纹苔痕、草叶泥土、砂砾风纹及薄雪岩面细节；提示词见 art_assets/battlefields/prompts/。修仙英雄有肉身指挥官时隐藏场边重复形象与旗帜。wuxia-art-preview.json 已配置剑修三功法、体修震地与150灵力，功法栏由原生自动填充。只通过 simulate.py --play 的战斗模拟器入口进行图形验证。
