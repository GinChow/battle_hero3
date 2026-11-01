"""2026-11-01 · Codex：检查武侠兵种的可部署资源及完整动作契约。"""
import json
from pathlib import Path
import struct
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "engine/Mods/cultivation/Content"


class WuxiaAssetTests(unittest.TestCase):
    def test_active_marker_sequence_is_complete_and_animated(self):
        manifest = json.loads((CONTENT.parent / "active-unit-art.json").read_text())
        data = json.loads((CONTENT / "Sprites/cultivation/active-unit.json").read_text())
        self.assertEqual(manifest["fps"], 15)
        self.assertEqual(len(data["sequences"]), 1)
        sequence = data["sequences"][0]
        self.assertEqual(sequence["group"], 0)
        self.assertEqual(len(sequence["frames"]), manifest["exportedFrames"])
        images = []
        for frame in sequence["frames"]:
            path = CONTENT / "Sprites" / data["basepath"] / frame
            self.assert_png_size(path, tuple(manifest["frameSize"]))
            images.append(path.read_bytes())
        self.assertGreater(len(set(images)), 1)

    def test_creatures_resolve_complete_animation_groups_and_portraits(self):
        creatures = json.loads((CONTENT / "config/creatures.json").read_text())
        manifest = json.loads((CONTENT.parent / "wuxia-art.json").read_text())
        for entry in manifest["characters"]:
            with self.subTest(creature=entry["creature"]):
                graphics = creatures[entry["creature"]]["graphics"]
                for creature in entry.get("creatures", [entry["creature"]]):
                    self.assertEqual(creatures[creature]["graphics"], graphics)
                animation = CONTENT / "Sprites" / (graphics["animation"] + ".json")
                data = json.loads(animation.read_text())
                groups = {seq["group"]: seq["frames"] for seq in data["sequences"]}
                rate = graphics["animationTime"]["frameRate"]
                self.assertEqual(rate, entry["framesPerSecond"])
                self.assertEqual(graphics["animationTime"]["idle"], rate)
                self.assertEqual(graphics["animationTime"]["walk"], 1.0)
                for group in (0, 1, 2, 3, 4, 5, 11, 12, 13, 18):
                    self.assertAlmostEqual(
                        len(groups[group]) / rate,
                        entry["referenceGroupFrames"][str(group)] / entry["referenceFrameRate"],
                        delta=0.5 / rate + 1e-9,
                    )
                for sequence in data["sequences"]:
                    self.assertFalse(sequence.get("generateShadow", 0))
                    self.assertFalse(sequence.get("generateOverlay", 0))
                self.assertTrue({0, 1, 2, 3, 4, 5, 7, 8, 11, 12, 13, 18, 22}.issubset(groups))
                for group in (0, 2, 3, 5, 12):
                    self.assertGreater(len(set(groups[group])), 1)
                self.assertEqual(groups[5][-1], groups[22][0])
                for frame in {f for sequence in groups.values() for f in sequence}:
                    file = CONTENT / "Sprites" / data["basepath"] / frame
                    self.assert_png_size(file, (450, 400))
                    for layer in ("SHADOW", "OVERLAY"):
                        self.assert_png_size(file.with_stem(file.stem + "-" + layer), (450, 400))
                for field, size in (("iconSmall", (32, 32)), ("iconLarge", (58, 64))):
                    self.assert_png_size(CONTENT / "Sprites" / graphics[field], size)

    def test_hero_portraits_and_battle_phases_cover_all_schools(self):
        heroes = json.loads((CONTENT / "config/heroes.json").read_text())
        for school in ("sword", "body", "demon", "talisman"):
            with self.subTest(school=school):
                hero = heroes[school + "Master"]
                self.assertEqual(hero["battleAnimationFrameRate"], 15)
                data = json.loads((CONTENT / "Sprites" / (hero["battleImage"] + ".json")).read_text())
                groups = {s["group"]: s["frames"] for s in data["sequences"]}
                self.assertEqual(set(groups), {0, 1, 2, 3, 4})
                self.assertEqual(len(groups[4]) / hero["battleAnimationFrameRate"], 0.8)
                for frame in {f for frames in groups.values() for f in frames}:
                    file = CONTENT / "Sprites" / data["basepath"] / frame
                    self.assert_png_size(file, (450, 400))
                    self.assert_png_size(file.with_stem(file.stem + "-SHADOW"), (450, 400))
                for kind, size in (("small", (48, 32)), ("large", (58, 64))):
                    self.assert_png_size(CONTENT / "Sprites" / hero["images"][kind], size)

    def assert_png_size(self, file, size):
        raw = file.read_bytes()
        self.assertEqual(raw[:8], b"\x89PNG\r\n\x1a\n", str(file))
        self.assertEqual(struct.unpack(">II", raw[16:24]), size, str(file))
        self.assertEqual(raw[25], 6, str(file))


if __name__ == "__main__":
    unittest.main()
