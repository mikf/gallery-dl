#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Generate zsh completion script from gallery-dl's argument parser"""

import util
import argparse
from gallery_dl import option

TEMPLATE = """#compdef gallery-dl

local curcontext="$curcontext"
typeset -A opt_args

local rc=1
_arguments -s -S \\
%(opts)s && rc=0

return rc
"""

TR = str.maketrans({
    "'": "'\\''",
    "[": "\\[",
    "]": "\\]",
})


opts = []
for action in option.build_parser()._actions:

    if not action.option_strings or action.help == argparse.SUPPRESS:
        continue
    elif len(action.option_strings) == 1:
        opt = action.option_strings[0]
    else:
        opt = "{" + ",".join(action.option_strings) + "}"

    opt += "'[" + action.help.translate(TR) + "]'"

    if action.metavar:
        opt += ":'<" + action.metavar.lower() + ">'"
        if action.metavar in ("FILE", "CFG", "DEST"):
            opt += ":_files"

    opts.append(opt)


PATH = util.path("data/completion/_gallery-dl")
with util.lazy(PATH) as file:
    file.write(TEMPLATE % {"opts": " \\\n".join(opts)})
