# -*- coding: utf-8 -*-

# Copyright 2015-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Global configuration module"""

import os
import sys
import json
import logging
from . import util

log = logging.getLogger("config")


# --------------------------------------------------------------------
# internals

_config = {"__global__": {}}
_warn_legacy = True

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


def load(files=None, strict=False, fmt="json"):
    """Load JSON configuration files"""
    if fmt == "yaml":
        try:
            import yaml
            load = yaml.safe_load
        except ImportError:
            log.error("Could not import 'yaml' module")
            return
    else:
        load = json.load

    for path in files or _default_configs:
        path = util.expand_path(path)
        try:
            with open(path, encoding="utf-8") as fp:
                config_dict = load(fp)
        except OSError as exc:
            if strict:
                log.error(exc)
                sys.exit(1)
        except Exception as exc:
            log.warning("Could not parse '%s': %s", path, exc)
            if strict:
                sys.exit(2)
        else:
            if "extractor" in config_dict:
                if _warn_legacy:
                    log.warning("Legacy config file found at %s", path)
                    log.warning("Run 'gallery-dl --config-update' or follow "
                                "<link> to update to the new format")
                config_dict = update_config_dict(config_dict)

            if not _config:
                _config.update(config_dict)
            else:
                util.combine_dict(_config, config_dict)


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


def config_init():
    paths = [
        util.expand_path(path)
        for path in _default_configs
    ]

    for path in paths:
        if os.access(path, os.R_OK):
            log.error("There is already a configuration file at %s", path)
            return 1

    for path in paths:
        try:
            with open(path, "w", encoding="utf-8") as fp:
                fp.write("""\
{
    "general": {

    },
    "downloader": {

    },
    "output": {

    }
}
""")
            break
        except OSError as exc:
            log.debug(exc)
    else:
        log.error("Unable to create a new configuration file "
                  "at any of the default paths")
        return 1

    log.info("Created a basic configuration file at %s", path)


def config_open():
    for path in _default_configs:
        path = util.expand_path(path)
        if os.access(path, os.R_OK | os.W_OK):
            import subprocess
            import shutil

            openers = (("explorer", "notepad")
                       if util.WINDOWS else
                       ("xdg-open", "open", os.environ.get("EDITOR", "")))
            for opener in openers:
                if opener := shutil.which(opener):
                    break
            else:
                log.warning("Unable to find a program to open '%s' with", path)
                return 1

            log.info("Running '%s %s'", opener, path)
            return subprocess.Popen((opener, path)).wait()

    log.warning("Unable to find any writable configuration file")
    return 1


def config_status():
    for path in _default_configs:
        path = util.expand_path(path)
        try:
            with open(path, encoding="utf-8") as fp:
                config_dict = json.load(fp)
        except FileNotFoundError:
            status = "NOT PRESENT"
        except ValueError:
            status = "INVALID JSON"
        except Exception as exc:
            log.debug(exc)
            status = "UNKNOWN"
        else:
            status = "OK"
            if "extractor" in config_dict:
                status += " (legacy)"
        print(f"{path}: {status}")


def config_update():
    for path in _default_configs:
        path = util.expand_path(path)
        try:
            with open(path, encoding="utf-8") as fp:
                config_content = fp.read()
            config_dict = json.loads(config_content)
        except Exception as exc:
            log.debug(exc)
        else:
            if "extractor" in config_dict:
                config_dict = update_config_dict(config_dict)

                # write backup
                with open(path + ".bak", "w", encoding="utf-8") as fp:
                    fp.write(config_content)

                # overwrite with updated JSON
                with open(path, "w", encoding="utf-8") as fp:
                    json.dump(
                        config_dict, fp,
                        indent=4,
                        ensure_ascii=get("output", "ascii"),
                    )

                log.info("Updated %s", path)
                log.info("Backup at %s", path + ".bak")


def update_config_dict(config_legacy):
    # option names  that could be a dict
    optnames = {"filename", "directory", "path-restrict", "cookies",
                "extension-map", "keywords", "keywords-default", "proxy"}

    config = {"general": {}}

    if extractor := config_legacy.pop("extractor", None):
        for key, value in extractor.items():
            if isinstance(value, dict) and key not in optnames:
                config[key] = value

                delete = []
                instances = None

                for skey, sval in value.items():
                    if isinstance(sval, dict):

                        # basecategory instance
                        if "root" in sval:
                            if instances is None:
                                config[key + ":instances"] = instances = {}
                            instances[skey] = sval
                            delete.append(skey)

                        # subcategory options
                        elif skey not in optnames:
                            config[f"{key}:{skey}"] = value[skey]
                            delete.append(skey)

                for skey in delete:
                    del value[skey]

                if not value:
                    del config[key]
            else:
                config["general"][key] = value

    if downloader := config_legacy.pop("downloader", None):
        config["downloader"] = downloader
        for module in ("http", "ytdl", "text"):
            if opts := downloader.pop(module, None):
                config["downloader:" + module] = opts

    for section_name in ("output", "postprocessor", "cache"):
        if section := config_legacy.pop(section_name, None):
            config[section_name] = section

    for key, value in config_legacy.items():
        config["general"][key] = value

    return config
