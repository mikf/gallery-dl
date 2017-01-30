# -*- coding: utf-8 -*-

# Copyright 2015, 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Global configuration module"""

import sys
import json
import os.path


# --------------------------------------------------------------------
# public interface

def load(*files, strict=False):
    """Load JSON configuration files"""
    configfiles = files or _default_configs
    for conf in configfiles:
        try:
            path = os.path.expanduser(os.path.expandvars(conf))
            with open(path) as file:
                confdict = json.load(file)
            _config.update(confdict)
        except FileNotFoundError:
            if strict:
                raise
            continue
        except ValueError as exception:
            print("Error while loading '", path, "':", sep="", file=sys.stderr)
            print(exception, file=sys.stderr)


def clear():
    """Reset configuration to en empty state"""
    globals()["_config"] = {}


def get(keys, default=None):
    """Get the value of property 'key' or a default-value if it doenst exist"""
    conf = _config
    try:
        for k in keys:
            conf = conf[k]
        return conf
    except (KeyError, AttributeError):
        return default


def interpolate(keys, default=None):
    """Interpolate the value of 'key'"""
    conf = _config
    try:
        for k in keys:
            default = conf.get(keys[-1], default)
            conf = conf[k]
        return conf
    except (KeyError, AttributeError):
        return default


def set(keys, value):
    """Set the value of property 'key' for this session"""
    conf = _config
    for k in keys[:-1]:
        try:
            conf = conf[k]
        except KeyError:
            temp = {}
            conf[k] = temp
            conf = temp
    conf[keys[-1]] = value


def setdefault(keys, value):
    """Set the value of property 'key' if it doesn't exist"""
    conf = _config
    for k in keys[:-1]:
        try:
            conf = conf[k]
        except KeyError:
            temp = {}
            conf[k] = temp
            conf = temp
    return conf.setdefault(keys[-1], value)


# --------------------------------------------------------------------
# internals

_config = {}

if os.name == "nt":
    _default_configs = [
        r"~\.config\gallery-dl\config.json",
        r"%USERPROFILE%\gallery-dl\config.json",
        r"~\.gallery-dl.conf",
        r"%USERPROFILE%\gallery-dl.conf",
    ]
else:
    _default_configs = [
        "/etc/gallery-dl.conf",
        "${HOME}/.config/gallery/config.json",
        "${HOME}/.config/gallery-dl/config.json",
        "${HOME}/.gallery-dl.conf",
    ]
