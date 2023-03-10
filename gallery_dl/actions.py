# -*- coding: utf-8 -*-

# Copyright 2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

""" """

import re
import sys
import logging
import operator
from . import util, exception


def parse(actionspec):
    if isinstance(actionspec, dict):
        actionspec = actionspec.items()

    actions = {}
    actions[logging.DEBUG] = actions_d = []
    actions[logging.INFO] = actions_i = []
    actions[logging.WARNING] = actions_w = []
    actions[logging.ERROR] = actions_e = []

    for event, spec in actionspec:
        level, _, pattern = event.partition(":")
        type, _, args = spec.partition(" ")
        action = (re.compile(pattern).search, ACTIONS[type](args))

        level = level.strip()
        if not level or level == "*":
            actions_d.append(action)
            actions_i.append(action)
            actions_w.append(action)
            actions_e.append(action)
        else:

            actions[_level_to_int(level)].append(action)

    return actions


def _level_to_int(level):
    try:
        return logging._nameToLevel[level]
    except KeyError:
        return int(level)


def action_print(opts):
    def _print(_):
        print(opts)
    return _print


def action_status(opts):
    op, value = re.match(r"\s*([&|^=])=?\s*(\d+)", opts).groups()

    op = {
        "&": operator.and_,
        "|": operator.or_,
        "^": operator.xor,
        "=": lambda x, y: y,
    }[op]

    value = int(value)

    def _status(args):
        args["job"].status = op(args["job"].status, value)
    return _status


def action_level(opts):
    level = _level_to_int(opts.lstrip(" ~="))

    def _level(args):
        args["level"] = level
    return _level


def action_wait(opts):
    def _wait(args):
        input("Press Enter to continue")
    return _wait


def action_restart(opts):
    return util.raises(exception.RestartExtraction)


def action_exit(opts):
    try:
        opts = int(opts)
    except ValueError:
        pass

    def _exit(args):
        sys.exit(opts)
    return _exit


ACTIONS = {
    "print"  : action_print,
    "status" : action_status,
    "level"  : action_level,
    "restart": action_restart,
    "wait"   : action_wait,
    "exit"   : action_exit,
}
