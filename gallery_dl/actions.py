# -*- coding: utf-8 -*-

# Copyright 2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

""" """

import re
import time
import logging
import operator
import functools
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
        search = re.compile(pattern).search if pattern else util.true

        if isinstance(spec, str):
            type, _, args = spec.partition(" ")
            action = (search, ACTIONS[type](args))
        else:
            action_list = []
            for s in spec:
                type, _, args = s.partition(" ")
                action_list.append(ACTIONS[type](args))
            action = (search, _chain_actions(action_list))

        level = level.strip()
        if not level or level == "*":
            actions_d.append(action)
            actions_i.append(action)
            actions_w.append(action)
            actions_e.append(action)
        else:
            actions[_level_to_int(level)].append(action)

    return actions


class LoggerAdapter():

    def __init__(self, logger, job):
        self.logger = logger
        self.extra = job._logger_extra
        self.actions = job._logger_actions

        self.debug = functools.partial(self.log, logging.DEBUG)
        self.info = functools.partial(self.log, logging.INFO)
        self.warning = functools.partial(self.log, logging.WARNING)
        self.error = functools.partial(self.log, logging.ERROR)

    def log(self, level, msg, *args, **kwargs):
        msg = str(msg)
        if args:
            msg = msg % args

        actions = self.actions[level]
        if actions:
            args = self.extra.copy()
            args["level"] = level

            for cond, action in actions:
                if cond(msg):
                    action(args)

            level = args["level"]

        if self.logger.isEnabledFor(level):
            kwargs["extra"] = self.extra
            self.logger._log(level, msg, (), **kwargs)


def _level_to_int(level):
    try:
        return logging._nameToLevel[level]
    except KeyError:
        return int(level)


def _chain_actions(actions):
    def _chain(args):
        for action in actions:
            action(args)
    return _chain


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


def action_exec(opts):
    def _exec(_):
        util.Popen(opts, shell=True).wait()
    return _exec


def action_wait(opts):
    if opts:
        seconds = util.build_duration_func(opts)

        def _wait(args):
            time.sleep(seconds())
    else:
        def _wait(args):
            input("Press Enter to continue")

    return _wait


def action_abort(opts):
    return util.raises(exception.StopExtraction)


def action_terminate(opts):
    return util.raises(exception.TerminateExtraction)


def action_restart(opts):
    return util.raises(exception.RestartExtraction)


def action_exit(opts):
    try:
        opts = int(opts)
    except ValueError:
        pass

    def _exit(args):
        raise SystemExit(opts)
    return _exit


ACTIONS = {
    "abort"    : action_abort,
    "exec"     : action_exec,
    "exit"     : action_exit,
    "level"    : action_level,
    "print"    : action_print,
    "restart"  : action_restart,
    "status"   : action_status,
    "terminate": action_terminate,
    "wait"     : action_wait,
}
