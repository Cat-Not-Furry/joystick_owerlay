import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "arcade", "engine"))

import config


def test_dev_user_dir_default():
	path = config.get_user_dir()
	assert "user" in path.replace("\\", "/")


def test_manifest_portable_user():
	mpath = os.path.join(ROOT, config.INSTALL_MANIFEST_FILENAME)
	data_dir = os.path.join(ROOT, "_test_portable_user")
	try:
		os.makedirs(data_dir, exist_ok=True)
		manifest = {
			"install_mode": "portable",
			"install_root": ROOT,
			"data_root": data_dir,
		}
		with open(mpath, "w", encoding="utf-8") as handle:
			json.dump(manifest, handle)
		# Reload USER_DIR-dependent paths
		assert config.get_user_dir() == data_dir
	finally:
		if os.path.isfile(mpath):
			os.remove(mpath)
		if os.path.isdir(data_dir):
			import shutil

			shutil.rmtree(data_dir, ignore_errors=True)


if __name__ == "__main__":
	test_dev_user_dir_default()
	test_manifest_portable_user()
	print("OK test_config_paths")
