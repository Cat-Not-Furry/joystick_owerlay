#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

import os
import platform
import sys

import engine_sys_path  # noqa: F401, E402

from config import (
	APP_ID,
	PRODUCT_DISPLAY_NAME,
	PROJECT_ROOT,
	ASSETS_DIR,
	BACKUP_PROFILES_ROOT,
	RESET_LOG_PATH,
	UPDATE_LOG_PATH,
	get_runtime_version,
	get_user_dir,
)


def _check_tkinter():
	try:
		import tkinter

		root = tkinter.Tk()
		root.withdraw()
		root.destroy()
		return True, "tkinter OK"
	except Exception as err:
		return False, f"tkinter: {err}"


def _check_pygame():
	try:
		import pygame

		pygame.init()
		if pygame.display.get_init():
			pygame.display.quit()
		pygame.quit()
		return True, f"pygame {pygame.version.ver}"
	except Exception as err:
		return False, str(err)


def _check_joystick():
	try:
		import pygame

		pygame.init()
		pygame.joystick.init()
		count = pygame.joystick.get_count()
		pygame.quit()
		return True, f"joysticks detectados: {count}"
	except Exception as err:
		return False, str(err)


def main():
	print(f"== {PRODUCT_DISPLAY_NAME} Doctor (Windows) ==")
	print(f"INFO Plataforma: {platform.system()} {platform.release()}")
	print(f"INFO Python: {sys.version.split()[0]}")
	print(f"INFO Proyecto: {PROJECT_ROOT}")
	print(f"INFO Versión: {get_runtime_version()}")
	print(f"INFO USER_DIR: {get_user_dir()}")
	print(f"INFO Espejo AppData: {BACKUP_PROFILES_ROOT}")
	print(f"INFO Reset log: {RESET_LOG_PATH}")
	print(f"INFO Update log: {UPDATE_LOG_PATH}")
	assets_ver = os.path.join(ASSETS_DIR, ".assets_version")
	if os.path.isfile(assets_ver):
		print(f"OK  Assets: {assets_ver}")
	else:
		print(f"ERR Falta {assets_ver}")

	ok, msg = _check_tkinter()
	print(("OK  " if ok else "WARN ") + msg)
	ok, msg = _check_pygame()
	print(("OK  " if ok else "ERR ") + msg)
	ok, msg = _check_joystick()
	print(("OK  " if ok else "WARN ") + msg)
	print(f"INFO APP_ID={APP_ID}")


if __name__ == "__main__":
	main()
