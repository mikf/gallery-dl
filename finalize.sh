#!/usr/bin/env bash
# -*- coding:utf-8 -*-

# --- 80 cols ---------------------------------------------------------------- #

python3 foliation.py "${1}"
asciidoc -a toc -a stylesheet="/home/user/Repos/gallery-dl-forked/custom.css" "${1}.adoc"

# END OF LINE

