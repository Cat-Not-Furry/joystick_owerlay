# install/windows/install_ops.py — operaciones de instalación (sin UI)

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PRODUCT_ID = "joystick-owerlay"
DISPLAY_NAME = "Joystick Owerlay"
MAIN_EXE = "joystick-overlay.exe"
UNINSTALL_EXE = "joystick-overlay-uninstall.exe"
SETUP_EXE = "joystick-overlay-setup.exe"
MANIFEST_NAME = "install_manifest.json"
APP_GUID = "{A1B2C3D4-E5F6-47AA-8899-001122334455}"


def default_installed_paths():
	program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
	install_root = Path(program_files) / DISPLAY_NAME
	local = os.environ.get("LOCALAPPDATA")
	if not local:
		local = str(Path.home() / "AppData" / "Local")
	data_root = Path(local) / "joystick_owerlay" / "user"
	return install_root, data_root


def detect_legacy_hud_owerlay() -> list[str]:
	found = []
	for env in ("APPDATA", "LOCALAPPDATA"):
		base = os.environ.get(env)
		if base:
			p = Path(base) / "hud_owerlay"
			if p.is_dir():
				found.append(str(p))
	return found


def validate_payload(root: Path) -> None:
	assets_ver = root / "arcade" / "assets" / ".assets_version"
	if not assets_ver.is_file():
		raise RuntimeError(f"Payload inválido: falta {assets_ver}")
	if not (root / "arcade" / "assets" / "icon_packs").is_dir():
		raise RuntimeError("Payload inválido: falta arcade/assets/icon_packs")


def extract_payload_archive(archive: Path, dest: Path) -> None:
	dest.mkdir(parents=True, exist_ok=True)
	if archive.suffix.lower() == ".zip":
		import zipfile

		with zipfile.ZipFile(archive, "r") as zf:
			zf.extractall(dest)
		return
	raise RuntimeError("Solo ZIP soportado en esta versión; use payload.7z pre-extraído o .zip")


def copy_tree(src: Path, dst: Path) -> None:
	if dst.exists():
		shutil.rmtree(dst)
	shutil.copytree(src, dst)


def write_manifest(
	install_root: Path,
	data_root: Path,
	install_mode: str,
	shortcuts: list | None = None,
	migration: dict | None = None,
	registry: dict | None = None,
) -> Path:
	manifest = {
		"manifest_version": 1,
		"product_id": PRODUCT_ID,
		"display_name": DISPLAY_NAME,
		"install_mode": install_mode,
		"install_root": str(install_root),
		"install_root_relative": ".",
		"data_root": str(data_root),
		"data_root_relative": "user" if install_mode == "portable" else None,
		"runtime": {
			"main_exe": MAIN_EXE,
			"uninstall_exe": UNINSTALL_EXE,
			"setup_exe": SETUP_EXE,
		},
		"shortcuts": shortcuts or [],
		"registry": registry or {"registered": False, "uninstall_key": None},
		"migration": migration or {"imported_from_hud_owerlay": False, "source_paths": []},
		"options": {},
		"installed_at": datetime.now(timezone.utc).isoformat(),
	}
	path = install_root / MANIFEST_NAME
	with open(path, "w", encoding="utf-8") as handle:
		json.dump(manifest, handle, indent=2)
	return path


def register_uninstall_arp(install_root: Path, version: str = "1.0.0") -> None:
	uninst = install_root / UNINSTALL_EXE
	key = rf"HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\{APP_GUID}"
	subprocess.run(
		[
			"reg",
			"add",
			key,
			"/f",
			"/v",
			"DisplayName",
			"/t",
			"REG_SZ",
			"/d",
			DISPLAY_NAME,
		],
		check=False,
	)
	subprocess.run(
		["reg", "add", key, "/f", "/v", "DisplayVersion", "/t", "REG_SZ", "/d", version],
		check=False,
	)
	subprocess.run(
		[
			"reg",
			"add",
			key,
			"/f",
			"/v",
			"InstallLocation",
			"/t",
			"REG_SZ",
			"/d",
			str(install_root),
		],
		check=False,
	)
	subprocess.run(
		[
			"reg",
			"add",
			key,
			"/f",
			"/v",
			"UninstallString",
			"/t",
			"REG_SZ",
			"/d",
			f'"{uninst}"',
		],
		check=False,
	)


def create_shortcut_vbs(
	target_exe: Path,
	arguments: str,
	shortcut_path: Path,
	description: str,
	icon_path: Path | None = None,
) -> None:
	shortcut_path.parent.mkdir(parents=True, exist_ok=True)
	script = Path(__file__).resolve().parent / "_create_shortcut.vbs"
	vbs = f"""
Set oWS = WScript.CreateObject("WScript.Shell")
Set oLink = oWS.CreateShortcut("{shortcut_path}")
oLink.TargetPath = "{target_exe}"
oLink.Arguments = "{arguments}"
oLink.WorkingDirectory = "{target_exe.parent}"
oLink.Description = "{description}"
"""
	if icon_path and icon_path.is_file():
		vbs += f'oLink.IconLocation = "{icon_path},0"\n'
	vbs += "oLink.Save\n"
	script.write_text(vbs, encoding="utf-8")
	subprocess.run(["cscript", "//nologo", str(script)], check=False)


def install_shortcuts(install_root: Path, icon: Path | None = None) -> list[dict]:
	start_menu = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / DISPLAY_NAME
	exe = install_root / MAIN_EXE
	entries = [
		("hud", "", "Joystick Owerlay"),
		("config", "config", "Joystick Owerlay — Configuración"),
		("tournament", "tournament", "Joystick Owerlay — Torneo"),
	]
	shortcuts = []
	for sid, args, title in entries:
		lnk = start_menu / f"{title}.lnk"
		create_shortcut_vbs(exe, args, lnk, title, icon)
		shortcuts.append({"id": sid, "name": title, "arguments": args or "run", "path": str(lnk)})
	return shortcuts


def migrate_from_legacy(source_roots: list[str], data_root: Path) -> None:
	for root in source_roots:
		src_user = Path(root) / "user"
		if not src_user.is_dir():
			src_user = Path(root)
		if not src_user.is_dir():
			continue
		data_root.mkdir(parents=True, exist_ok=True)
		for item in src_user.iterdir():
			dst = data_root / item.name
			if item.is_dir():
				shutil.copytree(item, dst, dirs_exist_ok=True)
			else:
				shutil.copy2(item, dst)
		break
