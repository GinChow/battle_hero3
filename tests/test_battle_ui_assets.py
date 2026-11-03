"""2026-11-02 · Codex：验证战斗皮肤资源、点击区和原生按钮状态契约。"""
import json
from pathlib import Path
import struct
import unittest
from PIL import Image, ImageChops, ImageFont


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "engine/Mods/cultivation/Content"


def load(path):
    return json.loads(path.read_text())


def png_size(path):
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"无效 PNG：{path}")
    return struct.unpack(">II", data[16:24])


class BattleUIAssetTests(unittest.TestCase):
    def test_school_selection_highlights_the_native_click_region(self):
        frames = load(CONTENT / 'Sprites/SPELTAB.json')['sequences'][0]['frames']
        # 原生帧序是风/火/水/土/全部，点击区域依次位于这五个纵坐标。
        for frame, row_y in zip(frames, (6, 122, 182, 63, 242)):
            for scale in (1, 2, 3):
                suffix = '' if scale == 1 else f'{scale}x'
                with Image.open(CONTENT / f'Sprites{suffix}' / frame) as active, \
                        Image.open(CONTENT / f'Data{suffix}/SpelTabNone.png') as idle:
                    bounds = ImageChops.difference(active.convert('RGBA'), idle.convert('RGBA')).convert('RGB').getbbox()
                    self.assertIsNotNone(bounds)
                    self.assertGreaterEqual(bounds[1], row_y * scale)
                    self.assertLessEqual(bounds[3], (row_y + 38) * scale)

    def test_window_skin_keeps_native_dimensions_and_all_three_densities(self):
        expected = {'DiBoxBck': (256, 256), 'SpelBack': (620, 595),
                    'SpellBookLarge': (800, 600), 'CPRESULT': (470, 561),
                    'cultivation/ui/y700-windows/settings': (600, 480),
                    'stackWindow/info-panel-0': (438, 187),
                    'stackWindow/spell-effects': (438, 42)}
        for name, size in expected.items():
            for scale in (1, 2, 3):
                folder = 'Data' if scale == 1 else f'Data{scale}x'
                self.assertEqual(png_size(CONTENT / folder / (name + '.png')),
                                 tuple(value * scale for value in size))

    def test_settings_actions_and_localized_labels_remain_available(self):
        config = load(CONTENT / 'config/widgets/settings/settingsMainContainer.json')
        items = {item.get('name'): item for item in config['items']}
        callbacks = {'loadButton': 'loadGame', 'saveButton': 'saveGame',
                     'restartButton': 'restartGame', 'mainMenuButton': 'returnToMainMenu',
                     'quitButton': 'quitGame', 'closeSettingsButton': 'closeWindow'}
        for name, callback in callbacks.items():
            item = items[name]
            self.assertEqual(item['callback'], callback)
            self.assertTrue(item['hotkey'])
            animation = load(CONTENT / 'Sprites' / (item['image'] + '.json'))
            frames = animation['sequences'][0]['frames']
            self.assertEqual(len(frames), 4)
            self.assertEqual(len({(CONTENT / 'Sprites' / frame).read_bytes() for frame in frames}), 4)
            for language in ('chinese', 'english'):
                labels = load(CONTENT / f'config/translations/ui-{language}.json')
                text = labels[item['items'][0]['text']]
                font = ImageFont.truetype(str(CONTENT / 'Data/cultivation/fonts/Zhizun.ttf'), 18)
                self.assertLessEqual(font.getlength(text), 92)
            self.assertLessEqual(item['position']['x'] + 100, 600)
            self.assertLessEqual(item['position']['y'] + 48, 480)

    def test_shared_controls_preserve_native_states_and_visible_selection(self):
        for name, count, size in [('SYSOPCHK', 2, (32, 24)), ('IGPCRDIV', 5, (16, 16)),
                                  ('OVBUTN2', 5, (16, 16)), ('SPELTAB', 5, (83, 294)),
                                  ('IOKAY', 4, (64, 30)), ('ICANCEL', 4, (64, 30)),
                                  ('settingsWindow/button32', 4, (32, 24)),
                                  ('stackWindow/upgradeButton', 4, (36, 36)),
                                  ('stackWindow/cancelButton', 4, (46, 20))]:
            frames = load(CONTENT / 'Sprites' / (name + '.json'))['sequences'][0]['frames']
            self.assertEqual(len(frames), count)
            self.assertEqual(len({(CONTENT / 'Sprites' / frame).read_bytes() for frame in frames}), count)
            for frame in frames:
                for scale in (1, 2, 3):
                    folder = 'Sprites' if scale == 1 else f'Sprites{scale}x'
                    self.assertEqual(png_size(CONTENT / folder / frame), tuple(v * scale for v in size))

    def test_spellbook_icons_match_quick_spell_art_and_native_canvas(self):
        spells = load(CONTENT / 'config/spells.json')
        for spell in load(CONTENT.parent / 'battle-ui-art.json')['spellIcons']:
            for scale in (1, 2, 3):
                folder = 'Data' if scale == 1 else f'Data{scale}x'
                with Image.open(CONTENT / folder / spells[spell]['graphics']['iconBook']) as art:
                    self.assertEqual(art.size, (78 * scale, 65 * scale))
                    self.assertEqual(art.convert('RGBA').getpixel((0, 0))[3], 0)
                    self.assertIsNotNone(art.getbbox())

    def test_character_hd_sequences_preserve_frames_and_have_all_layers(self):
        base = CONTENT / 'Sprites/cultivation/wuxia'
        for layout in base.glob('*.json'):
            config = load(layout)
            frames = {frame for sequence in config['sequences'] for frame in sequence['frames']}
            for scale in (2, 3):
                target = CONTENT / f'Sprites{scale}x/cultivation/wuxia'
                self.assertEqual(load(target / layout.name), config)
                for frame in frames:
                    source = Path(frame)
                    for suffix in ('', '-SHADOW', '-OVERLAY'):
                        name = source.with_stem(source.stem + suffix)
                        self.assertEqual(png_size(target / name), (450 * scale, 400 * scale))

    def test_hd_character_poses_keep_logical_bounds_and_transparency(self):
        for character in load(CONTENT.parent / 'wuxia-art.json')['characters']:
            name = Path(character['id']) / 'stand-000.png'
            with Image.open(CONTENT / 'Sprites/cultivation/wuxia' / name) as source:
                original = source.getbbox()
            for scale in (2, 3):
                with Image.open(CONTENT / f'Sprites{scale}x/cultivation/wuxia' / name) as source:
                    self.assertEqual(source.mode, 'RGBA')
                    self.assertEqual(source.getpixel((0, 0))[3], 0)
                    bounds = source.getbbox()
                    self.assertIsNotNone(bounds)
                    for actual, expected in zip(bounds, original):
                        self.assertLessEqual(abs(actual / scale - expected), 2)

    def test_body_font_and_number_boxes_fit_at_each_density(self):
        fonts = load(CONTENT / 'config/fonts.json')['trueType']
        tiny = fonts['TINY']
        self.assertGreaterEqual(tiny['size'][0], 11)
        self.assertNotEqual(tiny['file'], fonts['BIGFONT']['file'])
        for scale in (1, 2, 3):
            font = ImageFont.truetype(str(CONTENT / 'Data' / tiny['file']), tiny['size'][scale - 1])
            folder = 'Data' if scale == 1 else f'Data{scale}x'
            width, height = png_size(CONTENT / folder / 'combatUnitNumberWindowDefault.png')
            self.assertLessEqual(sum(font.getmetrics()), height - 2 * scale)
            self.assertLessEqual(font.getlength('999k'), width - 4 * scale)
            self.assertLessEqual(sum(font.getmetrics()), 14 * scale)

    def test_deployed_assets_have_matching_high_resolution_versions(self):
        manifest = load(CONTENT.parent / "battle-ui-art.json")
        for item in manifest["assets"]:
            with self.subTest(asset=item["name"]):
                for scale in item.get("scales", (1, 2)):
                    directory = item["folder"] + (f"{scale}x" if scale != 1 else "")
                    self.assertEqual(
                        png_size(CONTENT / directory / (item["name"] + ".png")),
                        (item["width"] * scale, item["height"] * scale),
                    )

    def test_configured_buttons_have_four_same_size_distinct_frames(self):
        config = load(CONTENT / "config/widgets/battleWindow2.json")
        for item in config["items"]:
            if item["type"] != "button":
                continue
            animation = load(CONTENT / "Sprites" / (item["image"] + ".json"))
            frames = animation["sequences"][0]["frames"]
            self.assertEqual(len(frames), 4)
            paths = [CONTENT / "Sprites" / animation["basepath"] / frame for frame in frames]
            self.assertEqual(len({png_size(file) for file in paths}), 1)
            self.assertEqual(len({file.read_bytes() for file in paths}), 4)

    def test_bottom_controls_keep_disjoint_hit_regions_and_native_actions(self):
        config = load(CONTENT / "config/widgets/battleWindow2.json")
        items = {item.get("name"): item for item in config["items"]}
        self.assertEqual(items["defence"]["hotkey"], "battleDefend")
        self.assertEqual(items["wait"]["hotkey"], "battleWait")
        self.assertEqual(items["cast"]["hotkey"], "battleCastSpell")
        names = ["options", "surrender", "flee", "autofight", "cast", "wait", "defence", "consoleUp", "consoleDown"]
        rectangles = []
        for name in names:
            item = items[name]
            animation = load(CONTENT / "Sprites" / (item["image"] + ".json"))
            first = animation["sequences"][0]["frames"][0]
            w, h = png_size(CONTENT / "Sprites" / animation["basepath"] / first)
            x, y = item["position"]["x"], item["position"]["y"]
            self.assertLessEqual(x + w, 800)
            self.assertLessEqual(y + h, 600)
            rectangles.append((name, x, y, w, h))
        rect = items["console"]["rect"]
        rectangles.append(("console", rect["x"], rect["y"], rect["w"], rect["h"]))
        for index, (name, x, y, w, h) in enumerate(rectangles):
            for other, ox, oy, ow, oh in rectangles[index + 1:]:
                self.assertFalse(x < ox + ow and ox < x + w and y < oy + oh and oy < y + h,
                                 f"点击区域重叠：{name} / {other}")

    def test_hex_masks_preserve_native_geometry(self):
        for name in ("CCELLSHD", "CCELLGRD", "UnitMovementHighlight", "UnitMaxMovementHighlight"):
            self.assertEqual(png_size(CONTENT / "Data" / (name + ".png")), (44, 56))

    def test_hex_tiles_cover_shared_edges_at_native_spacing(self):
        # 使用引擎的44/42间距和22错位，检查共边、三格交点及所有密度的漏缝。
        for scale in (1, 2, 3):
            directory = "Data" if scale == 1 else f"Data{scale}x"
            for name, minimum in (("cultivation/ui/jade/hex-hit", 128), ("CCELLSHD", 40),
                                  ("UnitMovementHighlight", 35), ("UnitMaxMovementHighlight", 30)):
                with self.subTest(scale=scale, asset=name):
                    with Image.open(CONTENT / directory / f"{name}.png") as image:
                        tile = image.convert("RGBA")
                    self.assertEqual(tile.size, (44 * scale, 56 * scale))
                    canvas = Image.new("RGBA", (242 * scale, 224 * scale))
                    for row in range(5):
                        for column in range(5):
                            x = (44 * column + (22 if row % 2 == 0 else 0)) * scale
                            canvas.alpha_composite(tile, (x, 42 * row * scale))
                    interior = canvas.getchannel("A").crop(tuple(v * scale for v in (66, 56, 198, 168)))
                    self.assertGreaterEqual(interior.getextrema()[0], minimum,
                                            "相邻六边形之间有透明缝隙或点击盲区")

    def test_retreat_and_surrender_use_distinct_art_and_actions(self):
        items = {item.get("name"): item for item in load(CONTENT / "config/widgets/battleWindow2.json")["items"]}
        self.assertEqual(items["flee"]["hotkey"], "battleRetreat")
        self.assertEqual(items["surrender"]["hotkey"], "battleSurrender")
        pictures = []
        for name in ("flee", "surrender"):
            animation = load(CONTENT / "Sprites" / (items[name]["image"] + ".json"))
            frame = animation["sequences"][0]["frames"][0]
            with Image.open(CONTENT / "Sprites" / animation["basepath"] / frame) as source:
                pictures.append(source.convert("RGBA").tobytes())
        self.assertNotEqual(*pictures)

    def test_cultivation_spell_icons_are_transparent_and_keep_native_frame_size(self):
        manifest = load(CONTENT.parent / "battle-ui-art.json")
        spells = load(CONTENT / "config/spells.json")
        for spell in manifest["spellIcons"]:
            for scale, directory in ((1, "Data"), (2, "Data2x")):
                with Image.open(CONTENT / directory / spells[spell]["graphics"]["iconEffect"]) as source:
                    self.assertEqual(source.size, (48 * scale, 36 * scale))
                    alpha = source.getchannel("A")
                    self.assertEqual(alpha.getpixel((0, 0)), 0)
                    self.assertGreater(alpha.getextrema()[1], 0)

    def test_translucent_hex_visuals_do_not_disable_picking(self):
        # SDL 的透明判定阈值为 128；内部可点击，四角不可点击。
        for scale, directory in ((1, "Data"), (2, "Data2x")):
            with Image.open(CONTENT / directory / "cultivation/ui/jade/hex-hit.png") as source:
                hit = source.convert("RGBA")
            with Image.open(CONTENT / directory / "CCELLSHD.png") as source:
                shade = source.convert("RGBA")
            self.assertEqual(hit.size, shade.size)
            for x, y in ((22, 4), (22, 28), (4, 28), (40, 28), (22, 51)):
                self.assertGreaterEqual(hit.getpixel((x * scale, y * scale))[3], 128)
            for x, y in ((0, 0), (43, 0), (0, 55), (43, 55)):
                self.assertLess(hit.getpixel((x * scale, y * scale))[3], 128)
            self.assertLess(shade.getpixel((22 * scale, 28 * scale))[3], 128)
            self.assertGreater(shade.getpixel((22 * scale, 28 * scale))[3], 0)

    def test_new_button_text_has_english_and_chinese_localization(self):
        english = load(CONTENT / "config/translations/ui-english.json")
        chinese = load(CONTENT / "config/translations/ui-chinese.json")
        self.assertEqual(set(english), set(chinese))
        for item in load(CONTENT / "config/widgets/battleWindow2.json")["items"]:
            for label in item.get("items", []):
                for entry in label.get("items", [label]):
                    if "text" in entry:
                        self.assertIn(entry["text"], english)


if __name__ == "__main__":
    unittest.main()
