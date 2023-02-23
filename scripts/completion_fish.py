#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Generate fish completion script from gallery-dl's argument parser"""

import util
from gallery_dl import option


TEMPLATE = """complete -c gallery-dl -x
%(opts)s
"""

opts = []
for action in option.build_parser()._actions:
    if not action.option_strings:
        continue

    opt = "complete -c gallery-dl"

    if action.metavar:
        if action.metavar == "FILE":
            opt += " -r -F"
        elif action.metavar == "PATH":
            opt += " -x -a '(__fish_complete_directories)'"
        else:
            opt += " -x"

    for optstr in action.option_strings:
        if optstr.startswith("--"):
            opt += " -l '" + optstr[2:] + "'"
        else:
            opt += " -s '" + optstr[1:] + "'"

    opt += " -d '" + action.help.replace("'", '"') + "'"

    opts.append(opt)

PATH = util.path("data/completion/gallery-dl.fish")
with util.lazy(PATH) as file:
    file.write(TEMPLATE % {"opts": "\n".join(opts)})
