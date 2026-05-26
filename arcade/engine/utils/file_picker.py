# utils/file_picker.py
# Selectores de directorio y archivo ZIP (zenity, kdialog, tkinter)

import os
import shutil
import subprocess
import sys


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


def _pick_directory_zenity(initial_dir, title):
	zenity_path = shutil.which("zenity")
	if zenity_path is None:
		return None
	return _run_picker_command(
		[
			zenity_path,
			"--file-selection",
			"--directory",
			f"--title={title}",
			f"--filename={initial_dir}/",
		]
	)


def _pick_directory_kdialog(initial_dir, title):
	kdialog_path = shutil.which("kdialog")
	if kdialog_path is None:
		return None
	return _run_picker_command(
		[
			kdialog_path,
			"--title",
			title,
			"--getexistingdirectory",
			initial_dir,
		]
	)


def _pick_directory_tkinter(initial_dir, title):
	try:
		import tkinter as tk
		from tkinter import filedialog

		root = tk.Tk()
		root.withdraw()
		root.attributes("-topmost", True)
		selected = filedialog.askdirectory(title=title, initialdir=initial_dir)
		root.destroy()
		return _normalize_selected_path(selected)
	except Exception:
		return None


def pick_directory(title="Seleccionar carpeta", initial_dir=None):
	"""Selecciona un directorio. Retorna ruta o None si cancela."""
	if initial_dir is None:
		initial_dir = os.getcwd()
	resolved = os.path.abspath(initial_dir)
	if not os.path.isdir(resolved):
		resolved = os.getcwd()
	for picker in (_pick_directory_zenity, _pick_directory_kdialog, _pick_directory_tkinter):
		path = picker(resolved, title)
		if path:
			return path
	return None


def _pick_zip_zenity(initial_dir, title):
	zenity_path = shutil.which("zenity")
	if zenity_path is None:
		return None
	return _run_picker_command(
		[
			zenity_path,
			"--file-selection",
			f"--title={title}",
			f"--filename={initial_dir}/",
			"--file-filter=*.zip",
		]
	)


def _pick_zip_kdialog(initial_dir, title):
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
			"*.zip",
		]
	)


def _pick_zip_tkinter(initial_dir, title):
	try:
		import tkinter as tk
		from tkinter import filedialog

		root = tk.Tk()
		root.withdraw()
		root.attributes("-topmost", True)
		selected = filedialog.askopenfilename(
			title=title,
			initialdir=initial_dir,
			filetypes=[("Archivos ZIP", "*.zip"), ("Todos los archivos", "*.*")],
		)
		root.destroy()
		return _normalize_selected_path(selected)
	except Exception:
		return None


def pick_zip_file(title="Seleccionar perfil ZIP", initial_dir=None):
	"""Selecciona un archivo ZIP. Retorna ruta o None si cancela."""
	if initial_dir is None:
		initial_dir = os.getcwd()
	resolved = os.path.abspath(initial_dir)
	if not os.path.isdir(resolved):
		resolved = os.getcwd()
	for picker in (_pick_zip_zenity, _pick_zip_kdialog, _pick_zip_tkinter):
		path = picker(resolved, title)
		if path:
			return path
	return None
