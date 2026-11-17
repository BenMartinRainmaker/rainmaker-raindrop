#!/bin/bash
# Assemble web and email editions, their assets, and legacy URL aliases.
set -e
cd "$(dirname "$0")"
python3 stage.py "$@"
