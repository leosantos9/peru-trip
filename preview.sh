#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
python3 scripts/build.py
python3 scripts/validate.py
printf 'Preview: http://127.0.0.1:8765/\n'
python3 -m http.server 8765 --bind 127.0.0.1 --directory "$(pwd)/dist"
