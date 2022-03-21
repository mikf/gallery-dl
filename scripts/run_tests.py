#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import unittest

TEST_DIRECTORY = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test")

sys.path.insert(0, TEST_DIRECTORY)

if len(sys.argv) <= 1:
    TESTS = [
        file.rpartition(".")[0]
        for file in os.listdir(TEST_DIRECTORY)
        if file.startswith("test_") and file != "test_results.py"
    ]
else:
    TESTS = [
        name if name.startswith("test_") else "test_" + name
        for name in sys.argv[1:]
    ]


suite = unittest.TestSuite()

for test in TESTS:
    try:
        module = __import__(test)
    except ImportError:
        print("unable to import", test)
    else:
        tests = unittest.defaultTestLoader.loadTestsFromModule(module)
        suite.addTests(tests)

if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.errors or result.failures:
        sys.exit(1)
