import unittest

from profiles.hud_layout import normalize_hud_layout_section, resolve_hud_layout_offsets


class TestHudLayout(unittest.TestCase):
	def test_normalize_none(self):
		self.assertIsNone(normalize_hud_layout_section(None))
		self.assertIsNotNone(normalize_hud_layout_section({}))

	def test_normalize_valid_elements(self):
		raw = {
			"version": 1,
			"base_resolution": [375, 175],
			"elements": {
				"dirs_group": {"x": 80, "y": 90},
				"button_positions": {"LP": {"x": 200, "y": 50}},
			},
		}
		out = normalize_hud_layout_section(raw)
		self.assertIsNotNone(out)
		self.assertEqual(out["elements"]["dirs_group"]["x"], 80)

	def test_resolve_offsets_default_profile(self):
		profile = {"hud_layout": None, "controller_style": "default", "button_count": 6}
		lo = resolve_hud_layout_offsets(profile, 375, 175, "stick", 6)
		self.assertIn("dirs_offset", lo)
		self.assertEqual(len(lo["button_pixel_offsets"]), 6)


if __name__ == "__main__":
	unittest.main()
