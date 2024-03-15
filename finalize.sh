#!/usr/bin/env bash
# -*- coding:utf-8 -*-

# --- 80 cols ---------------------------------------------------------------- #

SCRIPT_DIR=$(dirname "$(realpath "${0}")")

python3 foliation.py "${1}"
asciidoc -a toc -a stylesheet="${SCRIPT_DIR}/custom.css" "${1}.adoc"

# END OF LINE

