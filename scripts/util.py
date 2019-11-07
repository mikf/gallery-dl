# -*- coding: utf-8 -*-

import sys
import os.path

ROOTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.realpath(ROOTDIR))


def path(*segments, join=os.path.join):
    result = join(ROOTDIR, *segments)
    os.makedirs(os.path.dirname(result), exist_ok=True)
    return result
