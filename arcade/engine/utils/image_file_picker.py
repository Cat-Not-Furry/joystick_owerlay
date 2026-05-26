import os
import shutil
import subprocess
import sys

import pygame


_ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".gif"}


def _is_linux():
	return sys.platform.startswith("linux")


def _normalize_selected_path(raw_output):
	if not isinstance(raw_output, str):
		return None
	value = raw_output.strip()
	if value == "":
		return None
	return value


def _run_picker_command(command):
	try:
		result = subprocess.run(command, capture_output=True, text=True, check=False)
		if result.returncode != 0:
			return None
		return _normalize_selected_path(result.stdout)
	except Exception:
		return None


def _pick_with_zenity(initial_dir, title):
	zenity_path = shutil.which("zenity")
	if zenity_path is None:
		return None
	return _run_picker_command(
		[
			zenity_path,
			"--file-selection",
			f"--title={title}",
			f"--filename={initial_dir}/",
		]
	)


def _pick_with_kdialog(initial_dir, title):
	kdialog_path = shutil.which("kdialog")
	if kdialog_path is None:
		return None
	return _run_picker_command(
		[
			kdialog_path,
			"--title",
			title,
			"--getopenfilename",
			initial_dir,
			"*.png *.jpg *.jpeg *.bmp *.webp *.gif",
		]
	)


def _pick_with_tkinter(initial_dir, title):
	try:
		import tkinter as tk
		from tkinter import filedialog

		root = tk.Tk()
		root.withdraw()
		root.attributes("-topmost", True)
		selected = filedialog.askopenfilename(
			title=title,
			initialdir=initial_dir,
			filetypes=[
				("Imagenes", "*.png *.jpg *.jpeg *.bmp *.webp *.gif"),
				("Todos los archivos", "*.*"),
			],
		)
		root.destroy()
		return _normalize_selected_path(selected)
	except Exception:
		return None


def pick_image_file_linux(initial_dir="icons", title="Seleccionar imagen"):
	if not _is_linux():
		return None

	resolved_dir = os.path.abspath(initial_dir)
	if not os.path.isdir(resolved_dir):
		resolved_dir = os.getcwd()

	for picker in (_pick_with_zenity, _pick_with_kdialog, _pick_with_tkinter):
		selected_path = picker(resolved_dir, title)
		if selected_path:
			return selected_path
	return None


def validate_image_resolution(file_path, max_width=512, max_height=512):
	if not file_path:
		return False, "No se selecciono un archivo."
	if not os.path.isfile(file_path):
		return False, "La ruta seleccionada no existe."

	extension = os.path.splitext(file_path)[1].lower()
	if extension not in _ALLOWED_EXTENSIONS:
		return False, "Formato no valido. Usa PNG/JPG/BMP/WEBP/GIF."

	try:
		surface = pygame.image.load(file_path)
		width, height = surface.get_size()
	except Exception:
		return False, "No se pudo abrir la imagen."

	if width > max_width or height > max_height:
		return False, f"Imagen invalida: maximo permitido {max_width}x{max_height}px."

	return True, ""


def pick_image_file_with_validation(initial_dir="icons", max_width=512, max_height=512):
	selected_path = pick_image_file_linux(initial_dir=initial_dir)
	if not selected_path:
		return None, ""

	is_valid, message = validate_image_resolution(
		file_path=selected_path,
		max_width=max_width,
		max_height=max_height,
	)
	if not is_valid:
		return None, message
	return selected_path, ""
