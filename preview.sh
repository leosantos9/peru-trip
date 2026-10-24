#!/usr/bin/env sh
set -eu
python3 -m http.server 8000 --directory dist
