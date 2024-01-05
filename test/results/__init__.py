# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import functools

__directory__ = os.path.dirname(__file__)


@functools.lru_cache(maxsize=None)
def tests(name):
    module = __import__(name, globals(), None, (), 1)
    return module.__tests__


def all():
    ignore = ("__init__.py", "__pycache__")
    for filename in os.listdir(__directory__):
        if filename not in ignore:
            yield from tests(filename[:-3])


def category(category):
    return tests(category.replace(".", ""))
