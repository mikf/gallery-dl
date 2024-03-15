#!/usr/bin/env bash
# -*- coding:utf-8 -*-

# --- 80 cols ---------------------------------------------------------------- #

python3 foliation.py "${1}" && asciidoc -a toc "${1}.adoc"

# END OF LINE

