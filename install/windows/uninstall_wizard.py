#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Desinstalador: lee install_manifest.json junto al ejecutable."""

import json
import shutil
import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

MANIFEST_NAME = "install_manifest.json"
BG = "#1a1b26"
FG = "#c0caf5"


def _manifest_path() -> Path:
	if getattr(sys, "frozen", False):
		root = Path(sys.executable).resolve().parent
	else:
		root = Path(__file__).resolve().parent.parent.parent
	return root / MANIFEST_NAME


def main():
	root = _manifest_path().parent
	mpath = root / MANIFEST_NAME
	if not mpath.is_file():
		print(f"No se encontró {mpath}")
		return 1
	with open(mpath, "r", encoding="utf-8") as handle:
		manifest = json.load(handle)

	win = tk.Tk()
	win.title("Desinstalar Joystick Owerlay")
	win.configure(bg=BG)
	delete_data = tk.BooleanVar(value=False)
	tk.Label(win, text="¿Eliminar también los datos de usuario?", bg=BG, fg=FG).pack(padx=20, pady=10)
	tk.Checkbutton(win, text=f"Borrar {manifest.get('data_root', '')}", variable=delete_data, bg=BG, fg=FG).pack()

	def _do():
		for sc in manifest.get("shortcuts", []):
			p = sc.get("path")
			if p and Path(p).is_file():
				Path(p).unlink(missing_ok=True)
		if delete_data.get():
			data = manifest.get("data_root")
			if data and Path(data).is_dir():
				shutil.rmtree(data, ignore_errors=True)
		# No borrar Program Files sin elevación; usuario puede borrar carpeta portable
		if manifest.get("install_mode") == "portable":
			ir = Path(manifest.get("install_root", root))
			if ir.is_dir() and messagebox.askyesno("Confirmar", f"¿Borrar carpeta completa?\n{ir}"):
				shutil.rmtree(ir, ignore_errors=True)
		messagebox.showinfo("Listo", "Desinstalación registrada. Revise Agregar o quitar programas si aplica.")
		win.destroy()

	tk.Button(win, text="Desinstalar", command=_do, bg="#f7768e", fg=BG).pack(pady=10)
	win.mainloop()
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
