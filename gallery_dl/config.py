# -*- coding: utf-8 -*-

# Copyright 2015-2022 Mike Fährmann
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

_config = {"__global__": {}}

if util.WINDOWS:
    _default_configs = [
        r"%APPDATA%\gallery-dl\config.json",
        r"%USERPROFILE%\gallery-dl\config.json",
        r"%USERPROFILE%\gallery-dl.conf",
    ]
else:
    _default_configs = [
        "/etc/gallery-dl.conf",
        "${XDG_CONFIG_HOME}/gallery-dl/config.json"
        if os.environ.get("XDG_CONFIG_HOME") else
        "${HOME}/.config/gallery-dl/config.json",
        "${HOME}/.gallery-dl.conf",
    ]


if getattr(sys, "frozen", False):
    # look for config file in PyInstaller executable directory (#682)
    _default_configs.append(os.path.join(
        os.path.dirname(sys.executable),
        "gallery-dl.conf",
    ))


# --------------------------------------------------------------------
# public interface

def load(files=None, strict=False, fmt="json"):
    """Load JSON configuration files"""
    if fmt == "yaml":
        try:
            import yaml
            parsefunc = yaml.safe_load
        except ImportError:
            log.error("Could not import 'yaml' module")
            return
    else:
        parsefunc = json.load

    for path in files or _default_configs:
        path = util.expand_path(path)
        try:
            with open(path, encoding="utf-8") as fp:
                confdict = parsefunc(fp)
        except OSError as exc:
            if strict:
                log.error(exc)
                sys.exit(1)
        except Exception as exc:
            log.warning("Could not parse '%s': %s", path, exc)
            if strict:
                sys.exit(2)
        else:
            if not _config:
                _config.update(confdict)
            else:
                util.combine_dict(_config, confdict)


def clear():
    """Reset configuration to an empty state"""
    _config.clear()
    _config["__global__"] = {}


def build_options_dict(keys, conf=_config):
    opts = {}
    update = opts.update
    for key in keys:
        if key in conf:
            update(conf[key])
    if "__global__" in conf:
        update(conf["__global__"])
    return opts


def build_extractor_options_dict(extr):
    ccat = extr.category
    bcat = extr.basecategory
    subcat = extr.subcategory

    if bcat:
        keys = (
            "general",
            bcat,
            bcat + ":" + subcat,
            ccat,
            ccat + ":" + subcat,
        )
    else:
        keys = (
            "general",
            ccat,
            ccat + ":" + subcat,
        )

    return build_options_dict(keys)


def build_module_options_dict(extr, package, module, conf=_config):
    ccat = extr.category
    bcat = extr.basecategory
    subcat = extr.subcategory
    module = package + ":" + module

    if bcat:
        keys = (
            package,
            module,
            bcat + ":" + package,
            bcat + ":" + module,
            bcat + ":" + subcat + ":" + package,
            bcat + ":" + subcat + ":" + module,
            ccat + ":" + package,
            ccat + ":" + module,
            ccat + ":" + subcat + ":" + package,
            ccat + ":" + subcat + ":" + module,
        )
    else:
        keys = (
            package,
            module,
            ccat + ":" + package,
            ccat + ":" + module,
            ccat + ":" + subcat + ":" + package,
            ccat + ":" + subcat + ":" + module,
        )

    return build_options_dict(keys)


def get(section, key, default=None, *, conf=_config):
    """Get the value of property 'key' or a default value"""
    try:
        return conf[section][key]
    except Exception:
        return default


def set(section, key, value, *, conf=_config):
    """Set the value of property 'key' for this session"""
    try:
        conf[section][key] = value
    except KeyError:
        conf[section] = {key: value}


def setdefault(section, key, value, *, conf=_config):
    """Set the value of property 'key' if it doesn't exist"""
    try:
        conf[section].setdefault(key, value)
    except KeyError:
        conf[section] = {key: value}


def unset(section, key, *, conf=_config):
    """Unset the value of property 'key'"""
    try:
        del conf[section][key]
    except Exception:
        pass


def interpolate(sections, key, default=None, *, conf=_config):
    if key in conf["__global__"]:
        return conf["__global__"][key]
    for section in sections:
        if section in conf and key in conf[section]:
            default = conf[section][key]
    return default


class apply():
    """Context Manager: apply a collection of key-value pairs"""

    def __init__(self, kvlist):
        self.original = []
        self.kvlist = kvlist

    def __enter__(self):
        for path, key, value in self.kvlist:
            self.original.append((path, key, get(path, key, util.SENTINEL)))
            set(path, key, value)

    def __exit__(self, etype, value, traceback):
        for path, key, value in self.original:
            if value is util.SENTINEL:
                unset(path, key)
            else:
                set(path, key, value)
