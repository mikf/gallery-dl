# -*- coding: utf-8 -*-

# Copyright 2016-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

__version__ = "1.23.3"

from . import cache
import subprocess
import os


@cache.memcache()
def current_git_head():
    try:
        out, err = subprocess.Popen(
            ("git", "rev-parse", "--short", "HEAD"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.path.dirname(os.path.abspath(__file__)),
        ).communicate()
        if out and not err:
            return out.decode().rstrip()
        return None
    except (OSError, subprocess.SubprocessError):
        return None
