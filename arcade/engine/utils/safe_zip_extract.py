# utils/safe_zip_extract.py — extracción de ZIP con límites y sin path traversal / symlinks

from __future__ import annotations

import os
import stat
import zipfile
from pathlib import Path, PurePosixPath


class SafeZipExtractError(ValueError):
	"""ZIP rechazado por política de seguridad o límites."""


def _zip_member_mode(info: zipfile.ZipInfo) -> int:
	return (info.external_attr >> 16) & 0xFFFF


def _is_zip_dir_entry(info: zipfile.ZipInfo, filename: str) -> bool:
	if filename.endswith("/"):
		return True
	is_dir_fn = getattr(info, "is_dir", None)
	return bool(is_dir_fn and is_dir_fn())


def _zip_member_is_symlink(info: zipfile.ZipInfo, filename: str) -> bool:
	if _is_zip_dir_entry(info, filename):
		return False
	mode = _zip_member_mode(info)
	if mode:
		return stat.S_ISLNK(mode)
	return False


def _zip_member_is_special_nonfile(info: zipfile.ZipInfo) -> bool:
	mode = _zip_member_mode(info)
	if not mode:
		return False
	return bool(
		stat.S_ISCHR(mode)
		or stat.S_ISBLK(mode)
		or stat.S_ISFIFO(mode)
		or stat.S_ISSOCK(mode)
	)


def _reject_bad_filename(filename: str) -> None:
	if not filename or filename.strip() == "":
		raise SafeZipExtractError("ZIP invalido: nombre de miembro vacio")
	if filename.startswith("/") or filename.startswith("\\"):
		raise SafeZipExtractError("ZIP invalido: ruta absoluta no permitida")
	if "\x00" in filename:
		raise SafeZipExtractError("ZIP invalido: NUL en nombre")
	parts = PurePosixPath(filename).parts
	for p in parts:
		if p == "..":
			raise SafeZipExtractError("ZIP invalido: componente .. en ruta")
		for ch in p:
			if ord(ch) < 32:
				raise SafeZipExtractError("ZIP invalido: caracter de control en nombre")


def extract_zip_safely(
	zip_path: str | os.PathLike[str],
	dest_dir: str | os.PathLike[str],
	*,
	max_members: int = 512,
	max_path_length: int = 240,
	max_uncompressed_file: int = 15 * 1024 * 1024,
	max_total_uncompressed: int = 80 * 1024 * 1024,
) -> None:
	"""
	Extrae un ZIP bajo dest_dir sin usar extractall.

	- Rechaza symlinks, dispositivos, FIFOs, sockets (modo Unix en ZipInfo).
	- Rechaza path traversal (..), rutas absolutas, ZIP cifrado.
	- Aplica límites de conteo y tamaño (anti ZIP bomb razonable para perfiles).
	"""
	dest_root = Path(dest_dir).resolve()
	dest_root.mkdir(parents=True, exist_ok=True)

	total_written = 0

	with zipfile.ZipFile(zip_path, "r") as zf:
		infolist = zf.infolist()
		if len(infolist) > max_members:
			raise SafeZipExtractError(
				f"ZIP invalido: demasiados miembros ({len(infolist)} > {max_members})"
			)

		for info in infolist:
			filename = info.filename
			_reject_bad_filename(filename)
			if len(filename) > max_path_length:
				raise SafeZipExtractError("ZIP invalido: ruta demasiado larga")

			if info.flag_bits & 0x1:
				raise SafeZipExtractError("ZIP invalido: miembro cifrado no soportado")

			if _zip_member_is_symlink(info, filename) or _zip_member_is_special_nonfile(info):
				raise SafeZipExtractError("ZIP invalido: symlinks o nodos especiales no permitidos")

			rel = PurePosixPath(filename)
			target_path = (dest_root / str(rel)).resolve()

			try:
				target_path.relative_to(dest_root)
			except ValueError as exc:
				raise SafeZipExtractError("ZIP invalido: path fuera del directorio destino") from exc

			if _is_zip_dir_entry(info, filename):
				target_path.mkdir(parents=True, exist_ok=True)
				continue

			uncompressed = int(info.file_size)
			if uncompressed > max_uncompressed_file:
				raise SafeZipExtractError("ZIP invalido: fichero demasiado grande")
			if total_written + uncompressed > max_total_uncompressed:
				raise SafeZipExtractError("ZIP invalido: tamano total descomprimido excede limite")

			target_path.parent.mkdir(parents=True, exist_ok=True)

			written = 0
			with zf.open(info, "r") as src, open(target_path, "wb") as dst:
				while True:
					chunk = src.read(65536)
					if not chunk:
						break
					written += len(chunk)
					if written > max_uncompressed_file:
						raise SafeZipExtractError("ZIP invalido: tamano real excede limite")
					dst.write(chunk)

			if written != uncompressed and uncompressed >= 0:
				# ZIP corrupto o truncado; ya escribimos basura — borrar fichero parcial
				try:
					os.unlink(target_path)
				except OSError:
					pass
				raise SafeZipExtractError("ZIP invalido: tamano no coincide con cabecera")

			total_written += written

			if os.path.islink(target_path):
				try:
					os.unlink(target_path)
				except OSError:
					pass
				raise SafeZipExtractError("ZIP invalido: enlace simbolico en destino")
