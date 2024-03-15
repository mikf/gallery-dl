#!/usr/bin/env bash
# -*- coding:utf-8 -*-

# --- 80 cols ---------------------------------------------------------------- #

SLEEP_VALUE="60s"

python3 begin.py \
    "https://twitter.com/${1}" \
    --exec "sleep ${SLEEP_VALUE}" \
    --cookies "cookies.txt" \
    ;

# END OF LINE

