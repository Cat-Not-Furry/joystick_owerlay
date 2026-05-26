#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import engine_sys_path  # noqa: F401, E402

from config import (
	APP_ID,
	ASSETS_DIR,
	PROJECT_ROOT,
	RESET_LOG_PATH,
	UPDATE_LOG_PATH,
	get_runtime_version,
)
from utils.safe_zip_extract import extract_zip_safely


UPDATE_WHITELIST = (
	"arcade",
	"configs",
	"main.py",
	"configure.py",
	"tournament.py",
	"cli.py",
	"doctor.py",
	"engine_sys_path.py",
	"README.md",
	"docs",
	"install",
)


def print_help():
	print(
		f"""{APP_ID} — Joystick Owerlay (Windows)

Uso:
	joystick-overlay [comando]

Comandos:
	run            HUD principal
	config         Configuración de perfiles
	tournament     Modo torneo
	doctor         Diagnóstico
	--version      Versión runtime
	--show-reset-log  Ruta del log de reset
	--update --zip <ruta>  Actualización desde ZIP (preserva user/)
	-h, --help     Esta ayuda
"""
	)


def _log_update(action, result, message):
	os.makedirs(os.path.dirname(UPDATE_LOG_PATH), exist_ok=True)
	ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
	with open(UPDATE_LOG_PATH, "a", encoding="utf-8") as handle:
		handle.write(f"{ts} | {action} | {result} | {message}\n")


def _validate_update_root(root):
	assets_version = Path(root) / "arcade" / "assets" / ".assets_version"
	if not assets_version.is_file():
		raise RuntimeError("ZIP sin arcade/assets/.assets_version")
	icon_packs = Path(root) / "arcade" / "assets" / "icon_packs"
	if not icon_packs.is_dir():
		raise RuntimeError("ZIP sin arcade/assets/icon_packs")


def _apply_update_from_zip(zip_path):
	if not zip_path or not os.path.exists(zip_path):
		raise RuntimeError(f"ZIP no encontrado: {zip_path}")
	tmp_root = Path(UPDATE_LOG_PATH).parent / f"{APP_ID}_zip_update_tmp"
	if tmp_root.exists():
		shutil.rmtree(tmp_root, ignore_errors=True)
	tmp_root.mkdir(parents=True, exist_ok=True)
	try:
		extract_zip_safely(zip_path, str(tmp_root))
		candidates = [p for p in tmp_root.iterdir()]
		candidate_root = next((p for p in candidates if p.is_dir()), tmp_root)
		_validate_update_root(candidate_root)
		for name in UPDATE_WHITELIST:
			src = candidate_root / name
			if not src.exists():
				continue
			dst = Path(PROJECT_ROOT) / name
			if dst.exists():
				if dst.is_dir():
					shutil.rmtree(dst)
				else:
					dst.unlink()
			if src.is_dir():
				shutil.copytree(src, dst)
			else:
				shutil.copy2(src, dst)
	finally:
		shutil.rmtree(tmp_root, ignore_errors=True)


def run():
	from configure import main as run_config
	from doctor import main as run_doctor
	from main import main as run_main
	from tournament import main as run_tournament

	args = sys.argv[1:]
	if not args or args[0] in ("-h", "--help", "help"):
		print_help()
		return 0
	if args[0] == "--version":
		print(get_runtime_version() or "desconocida")
		return 0
	if args[0] == "--show-reset-log":
		try:
			with open(RESET_LOG_PATH, "r", encoding="utf-8") as handle:
				print(handle.read().strip() or "(reset log vacío)")
		except Exception:
			print(f"No existe reset log en {RESET_LOG_PATH}")
		return 0
	if args[0] == "--update":
		zip_path = None
		if "--zip" in args:
			idx = args.index("--zip")
			if idx + 1 < len(args):
				zip_path = args[idx + 1]
		try:
			if zip_path:
				_apply_update_from_zip(zip_path)
				_log_update("update_zip", "SUCCESS", zip_path)
				print("Actualización aplicada.")
			else:
				_log_update("update", "INFO", "sin --zip")
				print("Use --update --zip <ruta>")
			return 0
		except Exception as err:
			_log_update("update_zip", "ERROR", repr(err))
			print(f"Error: {err}")
			return 1
	cmd = args[0].strip().lower()
	if cmd == "run":
		run_main()
		return 0
	if cmd == "config":
		run_config()
		return 0
	if cmd == "tournament":
		run_tournament()
		return 0
	if cmd == "doctor":
		run_doctor()
		return 0
	print(f"Comando desconocido: {cmd}")
	print_help()
	return 1


if __name__ == "__main__":
	raise SystemExit(run())
