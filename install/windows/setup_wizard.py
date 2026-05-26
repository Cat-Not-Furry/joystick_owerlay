#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Asistente gráfico de instalación (tkinter)."""

import argparse
import shutil
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from install_ops import (
	DISPLAY_NAME,
	copy_tree,
	default_installed_paths,
	detect_legacy_hud_owerlay,
	extract_payload_archive,
	install_shortcuts,
	migrate_from_legacy,
	register_uninstall_arp,
	validate_payload,
	write_manifest,
)

BG = "#1a1b26"
FG = "#c0caf5"


class SetupWizard(tk.Tk):
	def __init__(self, register_only=False, payload_zip=None):
		super().__init__()
		self.title(f"{DISPLAY_NAME} — Instalación")
		self.configure(bg=BG)
		self.register_only = register_only
		self.payload_zip = Path(payload_zip) if payload_zip else None
		self.install_mode = tk.StringVar(value="installed")
		self.portable_dir = tk.StringVar(value=str(Path.home() / DISPLAY_NAME))
		self.migrate = tk.BooleanVar(value=bool(detect_legacy_hud_owerlay()))
		self.legacy_paths = detect_legacy_hud_owerlay()
		self._build()
		self.geometry("640x480")

	def _build(self):
		frm = tk.Frame(self, bg=BG, padx=16, pady=16)
		frm.pack(fill=tk.BOTH, expand=True)
		tk.Label(frm, text=DISPLAY_NAME, bg=BG, fg=FG, font=("Segoe UI", 16, "bold")).pack(anchor=tk.W)
		tk.Label(
			frm,
			text="Siguiente: elige modo, confirma rutas y registra accesos en el menú Inicio.",
			bg=BG,
			fg=FG,
			wraplength=580,
			justify=tk.LEFT,
		).pack(anchor=tk.W, pady=8)
		if not self.register_only:
			tk.Radiobutton(
				frm,
				text="Instalado (Program Files + datos en %LOCALAPPDATA%\\joystick_owerlay)",
				variable=self.install_mode,
				value="installed",
				bg=BG,
				fg=FG,
				selectcolor=BG,
			).pack(anchor=tk.W)
			tk.Radiobutton(
				frm,
				text="Portable (carpeta libre, user/ junto al programa)",
				variable=self.install_mode,
				value="portable",
				bg=BG,
				fg=FG,
				selectcolor=BG,
			).pack(anchor=tk.W)
			row = tk.Frame(frm, bg=BG)
			row.pack(fill=tk.X, pady=4)
			tk.Entry(row, textvariable=self.portable_dir, width=55, bg="#24283b", fg=FG, insertbackground=FG).pack(
				side=tk.LEFT, fill=tk.X, expand=True
			)
			tk.Button(row, text="Examinar…", command=self._browse, bg="#414868", fg=FG).pack(side=tk.LEFT, padx=4)
		if self.legacy_paths:
			tk.Checkbutton(
				frm,
				text="Importar perfiles de instalación hud_owerlay detectada",
				variable=self.migrate,
				bg=BG,
				fg=FG,
				selectcolor=BG,
			).pack(anchor=tk.W, pady=8)
		tk.Button(frm, text="Instalar", command=self._run, bg="#7aa2f7", fg="#1a1b26").pack(pady=16)

	def _browse(self):
		path = filedialog.askdirectory(title="Carpeta portable")
		if path:
			self.portable_dir.set(path)

	def _run(self):
		try:
			if self.install_mode.get() == "installed":
				install_root, data_root = default_installed_paths()
				install_root.mkdir(parents=True, exist_ok=True)
				data_root.mkdir(parents=True, exist_ok=True)
			else:
				install_root = Path(self.portable_dir.get())
				data_root = install_root / "user"
				install_root.mkdir(parents=True, exist_ok=True)
			if not self.register_only and self.payload_zip and self.payload_zip.is_file():
				tmp = install_root / "_payload_staging"
				if tmp.exists():
					shutil.rmtree(tmp)
				extract_payload_archive(self.payload_zip, tmp)
				children = [p for p in tmp.iterdir() if p.name != "__MACOSX"]
				src = children[0] if len(children) == 1 and children[0].is_dir() else tmp
				validate_payload(src)
				for item in src.iterdir():
					dest = install_root / item.name
					if item.is_dir():
						copy_tree(item, dest)
					else:
						shutil.copy2(item, dest)
				shutil.rmtree(tmp, ignore_errors=True)
			icon = Path(__file__).resolve().parent.parent / "joystick_overlay.ico"
			shortcuts = install_shortcuts(install_root, icon if icon.is_file() else None)
			migration = {"imported_from_hud_owerlay": False, "source_paths": []}
			if self.migrate.get() and self.legacy_paths:
				migrate_from_legacy(self.legacy_paths, data_root)
				migration = {"imported_from_hud_owerlay": True, "source_paths": self.legacy_paths}
			reg = {"registered": False, "uninstall_key": None}
			if self.install_mode.get() == "installed":
				register_uninstall_arp(install_root)
				reg["registered"] = True
			write_manifest(install_root, data_root, self.install_mode.get(), shortcuts, migration, reg)
			messagebox.showinfo("Listo", f"Completado en:\n{install_root}")
		except Exception as err:
			messagebox.showerror("Error", str(err))


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--register-only", action="store_true")
	parser.add_argument("--zip", dest="payload_zip")
	args = parser.parse_args()
	app = SetupWizard(register_only=args.register_only, payload_zip=args.payload_zip)
	app.mainloop()


if __name__ == "__main__":
	main()
