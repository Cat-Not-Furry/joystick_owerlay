"""Pruebas mínimas de extracción ZIP segura."""

import os
import sys
import tempfile
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "arcade", "engine"))

from utils.safe_zip_extract import SafeZipExtractError, extract_zip_safely


def test_rejects_path_traversal():
	with tempfile.TemporaryDirectory() as tmp:
		zpath = os.path.join(tmp, "bad.zip")
		with zipfile.ZipFile(zpath, "w") as zf:
			zf.writestr("../escape.txt", "x")
		dest = os.path.join(tmp, "out")
		os.makedirs(dest)
		try:
			extract_zip_safely(zpath, dest)
			assert False, "debía rechazar traversal"
		except SafeZipExtractError:
			pass


def test_extracts_regular_file():
	with tempfile.TemporaryDirectory() as tmp:
		zpath = os.path.join(tmp, "ok.zip")
		with zipfile.ZipFile(zpath, "w") as zf:
			zf.writestr("data/hello.txt", "hi")
		dest = os.path.join(tmp, "out")
		os.makedirs(dest)
		extract_zip_safely(zpath, dest)
		assert os.path.isfile(os.path.join(dest, "data", "hello.txt"))


if __name__ == "__main__":
	test_rejects_path_traversal()
	test_extracts_regular_file()
	print("OK test_zip_security")
