# config/config.py - Configuración del proyecto (Windows)

import json
import os
import sys
from pathlib import Path

APP_ID = "joystick_owerlay"
PRODUCT_DISPLAY_NAME = "Joystick Owerlay"
INSTALL_MANIFEST_FILENAME = "install_manifest.json"

_CONFIG_FILE = Path(__file__).resolve()
# Layout repo: <root>/arcade/engine/config/config.py
if (
	_CONFIG_FILE.parent.name == "config"
	and _CONFIG_FILE.parent.parent.name == "engine"
):
	_ENGINE_ROOT = _CONFIG_FILE.parent.parent
	_ARCADE_ROOT = _ENGINE_ROOT.parent
	PROJECT_ROOT = _ARCADE_ROOT.parent
	BASE_DIR = str(PROJECT_ROOT)
	ASSETS_DIR = str(_ARCADE_ROOT / "assets")
else:
	# Instalación plana antigua o site-packages sin árbol arcade
	PROJECT_ROOT = _CONFIG_FILE.parent.parent
	ASSETS_DIR = str(PROJECT_ROOT / "assets")

CONFIGS_DIR = str(Path(PROJECT_ROOT) / "configs")
ASSETS_VERSION_PATH = str(Path(ASSETS_DIR) / ".assets_version")
DEFAULT_ICON_PACK = "default"
ICON_PACKS_DIR = str(Path(ASSETS_DIR) / "icon_packs")
PROFILE_PRESETS_DIR = str(Path(ASSETS_DIR) / "profile_presets")
BINDING_TEMPLATES_DIR = str(Path(ASSETS_DIR) / "binding_templates")
PROFILE_KEY_BINDINGS_FILENAME = "key_bindings.json"
PROFILE_HITBOX_BINDINGS_FILENAME = "hitbox_bindings.json"
PROFILE_MIXBOX_BINDINGS_FILENAME = "mixbox_bindings.json"
PROFILE_JOYSTICK_BINDINGS_FILENAME = "joystick_bindings.json"


def _external_data_root():
	"""Espejo opcional bajo AppData (flag xdg_mirror_enabled en índice)."""
	if os.name == "nt":
		local = os.environ.get("LOCALAPPDATA")
		if local:
			return Path(local) / APP_ID
		return Path.home() / "AppData" / "Local" / APP_ID
	return Path.home() / ".local" / "share" / "joystick_overlay"


def _install_manifest_path():
	"""Manifiesto junto al ejecutable (PyInstaller) o raíz del proyecto en dev."""
	if getattr(os, "frozen", False):
		return Path(sys.executable).resolve().parent / INSTALL_MANIFEST_FILENAME
	return Path(PROJECT_ROOT) / INSTALL_MANIFEST_FILENAME


def _read_install_manifest():
	path = _install_manifest_path()
	if not path.is_file():
		return None
	try:
		with open(path, "r", encoding="utf-8") as handle:
			return json.loads(handle.read())
	except Exception:
		return None


def _legacy_hud_owerlay_roots():
	roots = []
	for env_name in ("APPDATA", "LOCALAPPDATA"):
		base = os.environ.get(env_name)
		if base:
			roots.append(str(Path(base) / "hud_owerlay"))
	return roots


# Canon dev / portable por defecto bajo proyecto.
PROJECT_USER_DIR = str(PROJECT_ROOT / "user")
LEGACY_XDG_USER_ROOT = str(_external_data_root() / "user")
BACKUP_PROFILES_ROOT = str(Path(LEGACY_XDG_USER_ROOT) / "profiles")
MIRROR_PROFILES_INDEX_PATH = str(Path(LEGACY_XDG_USER_ROOT) / "profiles_index.json")
LEGACY_APPDATA_USER_ROOTS = _legacy_hud_owerlay_roots()
RUNTIME_VERSION_PATH = str(Path(PROJECT_ROOT) / ".joystick_version")
HUD_VERSION_PATH = RUNTIME_VERSION_PATH  # alias legado


def get_assets_dir():
	return ASSETS_DIR


def get_user_dir():
	manifest = _read_install_manifest()
	if manifest:
		data_root = manifest.get("data_root")
		if data_root:
			return str(Path(data_root))
		install_root = manifest.get("install_root")
		rel = manifest.get("data_root_relative")
		if install_root and rel:
			return str(Path(install_root) / rel)
	mode = os.environ.get("JOYSTICK_STORAGE_MODE", "").strip().lower()
	if mode == "userdir" or (manifest and manifest.get("install_mode") == "installed"):
		return str(Path(_external_data_root()) / "user")
	return PROJECT_USER_DIR


USER_DIR = get_user_dir()

DATA_VERSION_PATH = str(Path(USER_DIR) / ".data_version")
RESET_LOG_PATH = str(Path(USER_DIR) / "reset.log")
UPDATE_LOG_PATH = str(Path(USER_DIR) / "update.log")
PROFILES_DIR = str(Path(USER_DIR) / "profiles")
PROFILES_INDEX_PATH = str(Path(USER_DIR) / "profiles_index.json")
PROFILES_PATH = PROFILES_INDEX_PATH
EXPORTS_DIR = str(Path(USER_DIR) / "exports")
USER_BACKUPS_DIR = str(Path(USER_DIR) / "backups")
JSON_DIR = USER_DIR
BASE_DIR = str(PROJECT_ROOT)


def get_runtime_version():
	try:
		with open(RUNTIME_VERSION_PATH, "r", encoding="utf-8") as file:
			value = file.read().strip()
			if value:
				return value
	except Exception:
		pass
	legacy = Path(PROJECT_ROOT) / "version.txt"
	try:
		with open(legacy, "r", encoding="utf-8") as file:
			return file.read().strip() or "0.0.0"
	except Exception:
		return "0.0.0"


def get_assets_version():
	try:
		with open(ASSETS_VERSION_PATH, "r", encoding="utf-8") as file:
			return file.read().strip()
	except Exception:
		return ""


def get_data_version(default_version="0"):
	try:
		with open(DATA_VERSION_PATH, "r", encoding="utf-8") as file:
			value = file.read().strip()
			return value if value else str(default_version)
	except Exception:
		return str(default_version)


def write_data_version(version):
	os.makedirs(USER_DIR, exist_ok=True)
	with open(DATA_VERSION_PATH, "w", encoding="utf-8") as file:
		file.write(str(version).strip() + "\n")


def ensure_contract_dirs():
	os.makedirs(ASSETS_DIR, exist_ok=True)
	os.makedirs(FONTS_DIR, exist_ok=True)
	os.makedirs(ICON_PACKS_DIR, exist_ok=True)
	os.makedirs(PROFILE_PRESETS_DIR, exist_ok=True)
	os.makedirs(BINDING_TEMPLATES_DIR, exist_ok=True)
	os.makedirs(USER_DIR, exist_ok=True)
	os.makedirs(PROFILES_DIR, exist_ok=True)
	os.makedirs(EXPORTS_DIR, exist_ok=True)
	os.makedirs(USER_BACKUPS_DIR, exist_ok=True)
	os.makedirs(BACKUP_PROFILES_ROOT, exist_ok=True)


# Ventana
WINDOW_CAPTION_APP = PRODUCT_DISPLAY_NAME
SCREEN_WIDTH = 375
SCREEN_HEIGHT = 175
MIN_WINDOW_WIDTH = 200
MIN_WINDOW_HEIGHT = 120
VIDEORESIZE_COOLDOWN_MS = 150
VIDEORESIZE_TOLERANCE_PX = 5
MIN_FONT_SIZE = 10
MAX_FONT_SIZE = 48
FPS = 60
TOURNAMENT_FPS = 30
MAX_JOYSTICK_RETRIES = 3

# Joystick
JOYSTICK_CENTER = (75, 85)
JOYSTICK_RADIUS = 50
JOYSTICK_STICK_LENGTH = 40

# Botón (radio constante)
BUTTON_RADIUS = 30

# Hitbox/Mixbox: márgenes para evitar solapamiento direccionales-botones
HITBOX_MIXBOX_DIRECTION_LEFT = 40
HITBOX_MIXBOX_BUTTONS_LEFT = 130
HITBOX_MIXBOX_GAP_BETWEEN_ZONES = 35
HITBOX_DIRECTION_DIAGONAL_STEP = 25

# Fila inferior Select/Start (mockup: bajo la rejilla de acción, centrados como par)
HUD_ROW1_Y = 44
HUD_ROW2_Y = 104
HUD_SYSTEM_ROW_Y = 158
HUD_SYSTEM_PAIR_SPREAD = 48

# Ruta para guardar bindings/perfiles (contrato user/)
BINDINGS_PATH = str(Path(USER_DIR) / "legacy_bindings.json")
JOYSTICK_BINDINGS_PATH = str(Path(USER_DIR) / "legacy_joystick_bindings.json")
PROFILES_PATH = PROFILES_INDEX_PATH
FONTS_DIR = str(Path(ASSETS_DIR) / "fonts")

# Filtro de nombre de dispositivo joystick
DEVICE_NAME_FILTER = ["joystick", "gamepad"]
SUPPORTED_BUTTON_COUNTS = [4, 6, 8]

# Estilos canónicos (UI y validación). Alias legados se normalizan al cargar.
CANONICAL_CONTROLLER_STYLES = frozenset({"default", "mvs", "cps", "ns", "ps", "xbox"})
SUPPORTED_CONTROLLER_STYLES = ["default", "mvs", "cps", "ns", "ps", "xbox"]
CONTROLLER_STYLE_ALIASES = {
	"playstation": "ps",
	"switch": "ns",
}

CONTROLLER_STYLE_TO_ICON_PACK = {
	"default": "default",
	"mvs": "mvs",
	"cps": "cps",
	"ns": "ns",
	"ps": "ps",
	"xbox": "xbox",
}

# Mapeo slot lógico (LP, MP, …) → nombre de archivo sin .png en el pack.
# None: usar minúsculas del label (compatible con pack default).
# MVS 8: archivos ab/ac/bd/cd son recurso visual por slot, no semántica combo.
_ICON_MVS_8 = {
	"LP": "a",
	"MP": "b",
	"HP": "c",
	"TR": "d",
	"LK": "ab",
	"MK": "ac",
	"HK": "bd",
	"BR": "cd",
}
_ICON_MVS_6 = {
	"LP": "a",
	"MP": "b",
	"HP": "c",
	"LK": "d",
	"MK": "ab",
	"HK": "ac",
}
_ICON_MVS_4 = {"LP": "a", "LK": "b", "HP": "c", "HK": "d"}

_ICON_CPS_8 = {
	"LP": "lp",
	"MP": "mp",
	"HP": "hp",
	"TR": "a1",
	"LK": "lk",
	"MK": "mk",
	"HK": "hk",
	"BR": "a2",
}
_ICON_CPS_6 = {
	"LP": "lp",
	"MP": "mp",
	"HP": "hp",
	"LK": "lk",
	"MK": "mk",
	"HK": "hk",
}
_ICON_CPS_4 = {"LP": "lp", "LK": "lk", "HP": "hp", "HK": "hk"}

_ICON_NS_4 = {"LP": "y", "LK": "b", "HP": "x", "HK": "a"}
_ICON_NS_6 = {
	"LP": "y",
	"MP": "x",
	"HP": "r",
	"LK": "b",
	"MK": "a",
	"HK": "zr",
}
_ICON_NS_8 = {
	"LP": "y",
	"MP": "x",
	"HP": "r",
	"TR": "l",
	"LK": "b",
	"MK": "a",
	"HK": "zr",
	"BR": "zl",
}

_ICON_PS_4 = {"LP": "squ", "LK": "x", "HP": "tri", "HK": "cir"}
_ICON_PS_6 = {
	"LP": "squ",
	"MP": "tri",
	"HP": "r1",
	"LK": "x",
	"MK": "cir",
	"HK": "r2",
}
_ICON_PS_8 = {
	"LP": "squ",
	"MP": "tri",
	"HP": "r1",
	"TR": "l1",
	"LK": "x",
	"MK": "cir",
	"HK": "r2",
	"BR": "l2",
}

_ICON_XBOX_4 = {"LP": "y", "LK": "a", "HP": "x", "HK": "b"}
_ICON_XBOX_6 = {
	"LP": "x",
	"MP": "y",
	"HP": "rb",
	"LK": "a",
	"MK": "b",
	"HK": "rt",
}
_ICON_XBOX_8 = {
	"LP": "x",
	"MP": "y",
	"HP": "rb",
	"TR": "lb",
	"LK": "a",
	"MK": "b",
	"HK": "rt",
	"BR": "lt",
}

ICON_MAPPING = {
	"default": None,
	"mvs": None,
	"cps": None,
	"ns": None,
	"ps": None,
	"xbox": None,
}


def _icon_map_for_pack_button_count(icon_pack, button_count):
	if icon_pack == "mvs":
		if button_count == 4:
			return _ICON_MVS_4
		if button_count == 8:
			return _ICON_MVS_8
		return _ICON_MVS_6
	if icon_pack == "cps":
		if button_count == 4:
			return _ICON_CPS_4
		if button_count == 8:
			return _ICON_CPS_8
		return _ICON_CPS_6
	if icon_pack == "ns":
		if button_count == 4:
			return _ICON_NS_4
		if button_count == 8:
			return _ICON_NS_8
		return _ICON_NS_6
	if icon_pack == "ps":
		if button_count == 4:
			return _ICON_PS_4
		if button_count == 8:
			return _ICON_PS_8
		return _ICON_PS_6
	if icon_pack == "xbox":
		if button_count == 4:
			return _ICON_XBOX_4
		if button_count == 8:
			return _ICON_XBOX_8
		return _ICON_XBOX_6
	return None


def icon_stem_for_label(icon_pack, label, button_count):
	"""Stem de PNG en el pack para el slot label (LP, …)."""
	m = _icon_map_for_pack_button_count(icon_pack, button_count)
	if not m:
		return str(label).strip().lower()
	return m.get(str(label).strip().upper(), str(label).strip().lower())


def normalize_controller_style(style):
	if style is None or style == "":
		return "default"
	s = str(style).strip().lower()
	if s in CONTROLLER_STYLE_ALIASES:
		return CONTROLLER_STYLE_ALIASES[s]
	if s in CANONICAL_CONTROLLER_STYLES:
		return s
	return "default"


def suggested_icon_pack_for_style(controller_style):
	return CONTROLLER_STYLE_TO_ICON_PACK.get(
		normalize_controller_style(controller_style), DEFAULT_ICON_PACK
	)


SUPPORTED_CAPTURE_MODES = ["normal", "obs_green"]
SUPPORTED_INPUT_MODES = ["teclado", "joystick", "hitbox", "mixbox"]
SUPPORTED_MONO_FONT_FAMILIES = ["JetBrainsMono", "FiraCode", "Hack"]
DEFAULT_MONO_FONT_FAMILY = "JetBrainsMono"

_fd = Path(ASSETS_DIR) / "fonts"
MONO_FONT_CONFIG = {
	"JetBrainsMono": {
		"regular_path": str(_fd / "JetBrainsMonoNerdFont-Regular.ttf"),
		"bold_path": str(_fd / "JetBrainsMonoNerdFont-Bold.ttf"),
		"system_name": "JetBrainsMono Nerd Font",
	},
	"FiraCode": {
		"regular_path": str(_fd / "FiraCodeNerdFont-Regular.ttf"),
		"bold_path": str(_fd / "FiraCodeNerdFont-Bold.ttf"),
		"system_name": "FiraCode Nerd Font",
	},
	"Hack": {
		"regular_path": str(_fd / "HackNerdFont-Regular.ttf"),
		"bold_path": str(_fd / "HackNerdFont-Bold.ttf"),
		"system_name": "Hack Nerd Font",
	},
}

# Easteregg: al presionar = sobre "Iniciar HUD" se abre otra instancia.
EASTEREGG_ENABLE_MULTI_INSTANCE = True
EASTEREGG_MULTI_INSTANCE_KEY = "equals"
EASTEREGG_MAX_INSTANCES = 3

# Colores
COLOR_BG = (0, 0, 0, 0)
COLOR_STICK = (100, 100, 100)
COLOR_STICK_KNOB = (0, 255, 0)
COLOR_BUTTON_INACTIVE = (80, 80, 80)
COLOR_BUTTON_ACTIVE = (255, 0, 0)
COLOR_TEXT = (255, 255, 255)
JOYSTICK_COLOR_PRESETS = {
	"verde": [0, 255, 0],
	"azul": [80, 160, 255],
	"rojo": [255, 70, 70],
	"morado": [180, 80, 255],
	"blanco": [240, 240, 240],
}
DEFAULT_HEX_COLOR = "#00FF00"

BUTTON_COLOR_PRESETS = {
	"gris_rojo": {"inactive": [80, 80, 80], "active": [255, 0, 0]},
	"gris_verde": {"inactive": [80, 80, 80], "active": [0, 255, 0]},
	"gris_azul": {"inactive": [80, 80, 80], "active": [80, 160, 255]},
	"oscuro_amarillo": {"inactive": [50, 50, 50], "active": [255, 220, 0]},
	"oscuro_blanco": {"inactive": [60, 60, 60], "active": [240, 240, 240]},
}


def get_button_labels(button_count):
	if button_count == 4:
		return ["LP", "LK", "HP", "HK"]
	if button_count == 8:
		return ["LP", "MP", "HP", "TR", "LK", "MK", "HK", "BR"]
	return ["LP", "MP", "HP", "LK", "MK", "HK"]


def get_bindings_format_key(button_count):
	if button_count == 4:
		return "formato_4"
	if button_count == 8:
		return "formato_8"
	return "formato_6"


def get_active_bindings_format_key(profile=None, button_count=None, layout_four_variant_4a=None):
	"""
	Clave de formato para bindings/HUD: formato_4a si 4 botones y variante 4A; si no, formato_4|6|8.
	Acepta un dict perfil o argumentos sueltos (para input_reader sin perfil completo).
	"""
	if isinstance(profile, dict):
		bc = int(profile.get("button_count", 6) or 6)
		four_a = bool(profile.get("layout_four_variant_4a")) and bc == 4
	else:
		bc = int(button_count if button_count is not None else 6)
		four_a = bool(layout_four_variant_4a) and bc == 4
	if four_a:
		return "formato_4a"
	return get_bindings_format_key(bc)


def get_hud_layout_variant_key(button_count, layout_four_variant_4a=False):
	"""Clave dentro de hud_layout.variants (alineada con get_active_bindings_format_key)."""
	bc = int(button_count or 6)
	if bc == 4 and layout_four_variant_4a:
		return "formato_4a"
	return get_bindings_format_key(bc)


def get_icon_paths(button_count):
	return [get_default_icon_path(label) for label in get_button_labels(button_count)]


def get_default_icon_path(label):
	return f"icons/{label.lower()}.png"


def get_hud_scale(screen_width, screen_height):
	scale_x = screen_width / SCREEN_WIDTH
	scale_y = screen_height / SCREEN_HEIGHT
	scale = min(scale_x, scale_y)
	return max(0.5, min(2.0, scale))


def get_system_button_positions(
	button_count,
	screen_width,
	screen_height,
	input_layout,
	controller_style=None,
	layout_four_variant_4a=False,
):
	"""
	Coordenadas en píxeles de pantalla para Select y Start (centro del icono).
	Se colocan bajo la rejilla de acción, como par centrado en el bloque de botones.
	input_layout: stick | hitbox | mixbox
	"""
	style = normalize_controller_style(controller_style)
	if input_layout in ("hitbox", "mixbox"):
		pts = get_button_positions_hitbox_mixbox(
			button_count,
			SCREEN_WIDTH,
			SCREEN_HEIGHT,
			controller_style=style,
			layout_four_variant_4a=layout_four_variant_4a,
		)
	else:
		pts = get_button_positions(
			button_count,
			SCREEN_WIDTH,
			SCREEN_HEIGHT,
			controller_style=style,
			layout_four_variant_4a=layout_four_variant_4a,
		)
	if not pts:
		mid = 260
	else:
		mid = sum(p[0] for p in pts) / len(pts)
	y_base = float(HUD_SYSTEM_ROW_Y)
	left = (int(mid - HUD_SYSTEM_PAIR_SPREAD), int(y_base))
	right = (int(mid + HUD_SYSTEM_PAIR_SPREAD), int(y_base))
	if screen_width is None or screen_height is None:
		return left, right
	scale = get_hud_scale(screen_width, screen_height)
	return (
		(int(left[0] * scale), int(left[1] * scale)),
		(int(right[0] * scale), int(right[1] * scale)),
	)


def _mvs_8_stick_positions_from_arcade_grid(full_positions):
	"""Rejilla 2x4 Neo Geo: A C AC AB / B D BD CD (misma geometría que ns/ps/xbox)."""
	return {
		"LP": full_positions["LP"],
		"MP": full_positions["LK"],
		"HP": full_positions["MP"],
		"TR": full_positions["MK"],
		"LK": full_positions["TR"],
		"MK": full_positions["HP"],
		"HK": full_positions["HK"],
		"BR": full_positions["BR"],
	}


# Índices en orden LP..BR: cada slot toma la coordenada que ocupaba el slot canónico perm[i].
_MVS_8_HITBOX_POSITION_PERM = (0, 4, 1, 5, 3, 2, 6, 7)


def layout_four_variant_4a_from_profile(profile):
	"""True si el perfil usa rejilla 4A (solo aplica con button_count == 4)."""
	if not isinstance(profile, dict):
		return False
	return bool(profile.get("layout_four_variant_4a", False))


def get_button_positions(
	button_count,
	screen_width=None,
	screen_height=None,
	controller_style=None,
	layout_four_variant_4a=False,
):
	base = _get_button_positions_base(
		button_count, controller_style, layout_four_variant_4a=layout_four_variant_4a
	)
	if screen_width is None or screen_height is None:
		return base
	scale = get_hud_scale(screen_width, screen_height)
	return [(int(x * scale), int(y * scale)) for x, y in base]


def _get_button_positions_base(
	button_count, controller_style=None, layout_four_variant_4a=False
):
	style = normalize_controller_style(controller_style)
	if button_count == 4:
		if layout_four_variant_4a:
			# Tres arriba (LP LK HP); HK debajo de LP — mockup MVS/CPS/… mismo mapa de slots.
			x1, x2, x3 = 195, 265, 335
			top_y, bot_y = float(HUD_ROW1_Y), float(HUD_ROW2_Y)
			full = {
				"LP": (x1, top_y),
				"LK": (x2, top_y),
				"HP": (x3, top_y),
				"HK": (x1, bot_y),
			}
			return [full[label] for label in get_button_labels(button_count)]
		return [
			(220, HUD_ROW1_Y),
			(220, HUD_ROW2_Y),
			(285, HUD_ROW1_Y),
			(285, HUD_ROW2_Y),
		]
	if button_count == 8:
		full_positions = {
			"LP": (165, HUD_ROW1_Y),
			"MP": (225, HUD_ROW1_Y),
			"HP": (285, HUD_ROW1_Y),
			"TR": (345, HUD_ROW1_Y),
			"LK": (165, HUD_ROW2_Y),
			"MK": (225, HUD_ROW2_Y),
			"HK": (285, HUD_ROW2_Y),
			"BR": (345, HUD_ROW2_Y),
		}
		if style == "mvs":
			full_positions = _mvs_8_stick_positions_from_arcade_grid(full_positions)
	else:
		full_positions = {
			"LP": (195, HUD_ROW1_Y),
			"MP": (265, HUD_ROW1_Y),
			"HP": (335, HUD_ROW1_Y),
			"LK": (195, HUD_ROW2_Y),
			"MK": (265, HUD_ROW2_Y),
			"HK": (335, HUD_ROW2_Y),
		}
	return [full_positions[label] for label in get_button_labels(button_count)]


def _get_button_positions_hitbox_mixbox_base(
	button_count, controller_style=None, layout_four_variant_4a=False
):
	dx = HITBOX_MIXBOX_BUTTONS_LEFT - 95
	dx_8 = 0
	style = normalize_controller_style(controller_style)
	if button_count == 4:
		if layout_four_variant_4a:
			x0 = 95 + dx
			step = 60
			xs = [x0, x0 + step, x0 + 2 * step]
			y1, y2 = float(HUD_ROW1_Y), float(HUD_ROW2_Y)
			return {
				"LP": (xs[0], y1),
				"LK": (xs[1], y1),
				"HP": (xs[2], y1),
				"HK": (xs[0], y2),
			}
		return {
			"LP": (210 + dx, 128),
			"LK": (260 + dx, 70),
			"HP": (330 + dx, 46),
			"HK": (400 + dx, 50),
		}
	if button_count == 8:
		out = {
			"LP": (95 + dx_8, 84),
			"MP": (165 + dx_8, 44),
			"HP": (235 + dx_8, 44),
			"TR": (345 + dx_8, 44),
			"LK": (95 + dx_8, 124),
			"MK": (165 + dx_8, 84),
			"HK": (235 + dx_8, 84),
			"BR": (345 + dx_8, 84),
		}
		if style == "mvs":
			labels = get_button_labels(8)
			canon = [out[l] for l in labels]
			perm = _MVS_8_HITBOX_POSITION_PERM
			for i, lbl in enumerate(labels):
				out[lbl] = canon[perm[i]]
		return out
	return {
		"LP": (95 + dx, 84),
		"MP": (195 + dx, 44),
		"HP": (295 + dx, 44),
		"LK": (95 + dx, 124),
		"MK": (195 + dx, 84),
		"HK": (295 + dx, 84),
	}


def get_button_positions_hitbox_mixbox(
	button_count,
	screen_width,
	screen_height,
	controller_style=None,
	layout_four_variant_4a=False,
):
	base = _get_button_positions_hitbox_mixbox_base(
		button_count, controller_style, layout_four_variant_4a=layout_four_variant_4a
	)
	labels = get_button_labels(button_count)
	positions = [base[label] for label in labels]
	if screen_width is None or screen_height is None:
		return positions
	scale = get_hud_scale(screen_width, screen_height)
	return [(int(x * scale), int(y * scale)) for x, y in positions]


def get_controller_button_name(label, controller_style):
	style = normalize_controller_style(controller_style)
	controller_maps = {
		"ps": {
			"LP": "Cuadrado",
			"MP": "Triangulo",
			"HP": "R1",
			"TR": "R2",
			"LK": "X",
			"MK": "Circulo",
			"HK": "L1",
			"BR": "L2",
		},
		"xbox": {
			"LP": "X",
			"MP": "Y",
			"HP": "RB",
			"TR": "RT",
			"LK": "A",
			"MK": "B",
			"HK": "LB",
			"BR": "LT",
		},
		"ns": {
			"LP": "Y",
			"MP": "X",
			"HP": "R",
			"TR": "ZR",
			"LK": "B",
			"MK": "A",
			"HK": "L",
			"BR": "ZL",
		},
		"mvs": {
			"LP": "A",
			"MP": "B",
			"HP": "C",
			"TR": "D",
			"LK": "AB",
			"MK": "AC",
			"HK": "BD",
			"BR": "CD",
		},
		"cps": {
			"LP": "LP",
			"MP": "MP",
			"HP": "HP",
			"TR": "A1",
			"LK": "LK",
			"MK": "MK",
			"HK": "HK",
			"BR": "A2",
		},
	}
	if style in controller_maps:
		return controller_maps[style].get(label, label)
	return label


PLAYSTATION_SYMBOLS = {
	"LP": "\u25a0",
	"MP": "\u25b2",
	"LK": "\u2715",
	"MK": "\u25cf",
	"HP": "R1",
	"TR": "R2",
	"HK": "L1",
	"BR": "L2",
}

XBOX_4_BUTTONS = {"LP": "A", "LK": "B", "HP": "Y", "HK": "X"}
NS_4_BUTTONS = {"LP": "B", "LK": "A", "HP": "X", "HK": "Y"}
PS_4_BUTTONS = {"LP": "\u25a0", "LK": "\u2715", "HP": "\u25b2", "HK": "\u25cf"}
MVS_4_BUTTONS = {"LP": "A", "LK": "B", "HP": "C", "HK": "D"}
CPS_4_BUTTONS = {"LP": "LP", "LK": "LK", "HP": "HP", "HK": "HK"}


def get_hud_fallback_text(label, controller_style, button_count=None):
	if str(label).strip().upper() == "SELECT":
		return "Select"
	if str(label).strip().upper() == "START":
		return "Start"
	style = normalize_controller_style(controller_style)
	if button_count == 4:
		if style == "ps":
			return PS_4_BUTTONS.get(label, label)
		if style == "xbox":
			return XBOX_4_BUTTONS.get(label, label)
		if style == "ns":
			return NS_4_BUTTONS.get(label, label)
		if style == "mvs":
			return MVS_4_BUTTONS.get(label, label)
		if style == "cps":
			return CPS_4_BUTTONS.get(label, label)
	short_maps = {
		"xbox": {"A": "A", "B": "B", "X": "X", "Y": "Y"},
		"ns": {"A": "A", "B": "B", "X": "X", "Y": "Y"},
	}
	if style == "ps":
		return PLAYSTATION_SYMBOLS.get(label, label)
	controller_name = get_controller_button_name(label, style)
	if style in short_maps:
		return short_maps[style].get(controller_name, controller_name)
	return label


def get_background_color(capture_mode):
	if capture_mode == "obs_green":
		return (0, 255, 0)
	return (0, 0, 0)


def normalize_mono_font_family(font_family):
	if font_family in SUPPORTED_MONO_FONT_FAMILIES:
		return font_family
	return DEFAULT_MONO_FONT_FAMILY


def get_mono_font_config(font_family):
	return MONO_FONT_CONFIG[normalize_mono_font_family(font_family)]


def parse_hex_color(color_text):
	if not isinstance(color_text, str):
		return None
	value = color_text.strip()
	if value.startswith("#"):
		value = value[1:]
	if len(value) != 6:
		return None
	try:
		return [int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)]
	except Exception:
		return None


def rgb_to_hex(color_values):
	if not isinstance(color_values, list) or len(color_values) != 3:
		return DEFAULT_HEX_COLOR
	return "#{:02X}{:02X}{:02X}".format(
		max(0, min(255, int(color_values[0]))),
		max(0, min(255, int(color_values[1]))),
		max(0, min(255, int(color_values[2]))),
	)
