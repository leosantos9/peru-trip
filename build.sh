#!/usr/bin/env sh
set -eu
python3 scripts/build.py
python3 scripts/validate.py
