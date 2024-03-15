#!/usr/bin/env bash
# -*- coding:utf-8 -*-

# --- 80 cols ---------------------------------------------------------------- #

SLEEP_VALUE="60s"

python3 foliation.py "${1}" && asciidoc -a toc "${1}.adoc"

# END OF LINE

