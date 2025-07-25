#!/bin/sh
cd `dirname $0`

. venv/bin/activate

# We use `python -m PyInstaller` as opposed to `pyinstaller` as the former
# runs in the venv and the latter does not
python -m PyInstaller --onefile src/main.py
tar -czvf dist/archive.tar.gz ./dist/main meta.json
# To run locally, we need meta.json in the same directory. So, add to dist/ a
# symlink that goes one directory up to meta.json
ln -s -f ../meta.json dist
