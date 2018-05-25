# -*- coding: utf-8 -*-

# Copyright 2015-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Global configuration module"""

import sys
import json
import os.path
import logging
from . import util

log = logging.getLogger("config")


# --------------------------------------------------------------------
# internals

_config = {}

if os.name == "nt":
    _default_configs = [
        r"%USERPROFILE%\gallery-dl\config.json",
        r"%USERPROFILE%\gallery-dl.conf",
    ]
else:
    _default_configs = [
        "/etc/gallery-dl.conf",
        "${HOME}/.config/gallery/config.json",
        "${HOME}/.config/gallery-dl/config.json",
        "${HOME}/.gallery-dl.conf",
    ]


# --------------------------------------------------------------------
# public interface

def load(*files, format="json", strict=False):
    """Load JSON configuration files"""
    configfiles = files or _default_configs

    if format == "yaml":
        try:
            import yaml
            parsefunc = yaml.safe_load
        except ImportError:
            log.error("Could not import 'yaml' module")
            return
    else:
        parsefunc = json.load

    for conf in configfiles:
        try:
            path = util.expand_path(conf)
            with open(path, encoding="utf-8") as file:
                confdict = parsefunc(file)
            if not _config:
                _config.update(confdict)
            else:
                util.combine_dict(_config, confdict)
        except FileNotFoundError:
            if strict:
                log.error("Configuration file '%s' not found", path)
                sys.exit(1)
        except Exception as exc:
            log.warning("Could not parse '%s':  %s", path, exc)
            if strict:
                sys.exit(2)


def clear():
    """Reset configuration to an empty state"""
    _config.clear()


def get(keys, default=None, conf=_config):
    """Get the value of property 'key' or a default value"""
    try:
        for k in keys:
            conf = conf[k]
        return conf
    except (KeyError, AttributeError):
        return default


def interpolate(keys, default=None, conf=_config):
    """Interpolate the value of 'key'"""
    try:
        lkey = keys[-1]
        if lkey in conf:
            return conf[lkey]
        for k in keys:
            if lkey in conf:
                default = conf[lkey]
            conf = conf[k]
        return conf
    except (KeyError, AttributeError):
        return default


def set(keys, value, conf=_config):
    """Set the value of property 'key' for this session"""
    for k in keys[:-1]:
        try:
            conf = conf[k]
        except KeyError:
            temp = {}
            conf[k] = temp
            conf = temp
    conf[keys[-1]] = value


def setdefault(keys, value, conf=_config):
    """Set the value of property 'key' if it doesn't exist"""
    for k in keys[:-1]:
        try:
            conf = conf[k]
        except KeyError:
            temp = {}
            conf[k] = temp
            conf = temp
    return conf.setdefault(keys[-1], value)


def unset(keys, conf=_config):
    """Unset the value of property 'key'"""
    try:
        for k in keys[:-1]:
            conf = conf[k]
        del conf[keys[-1]]
    except (KeyError, AttributeError):
        pass


class apply():
    """Context Manager to temporarily apply a collection of key-value pairs"""
    _sentinel = object()

    def __init__(self, kvlist):
        self.original = []
        self.kvlist = kvlist

    def __enter__(self):
        for key, value in self.kvlist:
            self.original.append((key, get(key, self._sentinel)))
            set(key, value)

    def __exit__(self, etype, value, traceback):
        for key, value in self.original:
            if value is self._sentinel:
                unset(key)
            else:
                set(key, value)
