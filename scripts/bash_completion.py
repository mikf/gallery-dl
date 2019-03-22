#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import sys
import os.path

ROOTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.realpath(ROOTDIR))

from gallery_dl import option  # noqa


TEMPLATE = """_gallery_dl()
{
    local cur prev
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    if [[ "${prev}" =~ ^(%(fileopts)s)$ ]]; then
        COMPREPLY=( $(compgen -f -- "${cur}") )
    elif [[ "${prev}" =~ ^(%(diropts)s)$ ]]; then
        COMPREPLY=( $(compgen -d -- "${cur}") )
    else
        COMPREPLY=( $(compgen -W "%(opts)s" -- "${cur}") )
    fi
}

complete -F _gallery_dl gallery-dl
"""

opts = []
diropts = []
fileopts = []
for action in option.build_parser()._actions:

    if action.metavar in ("DEST",):
        diropts.extend(action.option_strings)

    elif action.metavar in ("FILE", "CFG"):
        fileopts.extend(action.option_strings)

    for opt in action.option_strings:
        if opt.startswith("--"):
            opts.append(opt)


PATH = os.path.join(ROOTDIR, "gallery-dl.bash-completion")
with open(PATH, "w", encoding="utf-8") as file:
    file.write(TEMPLATE % {
        "opts"    : " ".join(opts),
        "diropts" : "|".join(diropts),
        "fileopts": "|".join(fileopts),
    })
