# -*- coding: utf-8 -*-

# Copyright 2015-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Global configuration module"""

import sys
import os.path
import logging
from . import util

log = logging.getLogger("config")


# --------------------------------------------------------------------
# internals

_config = {}
_files = []

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


if util.EXECUTABLE:
    # look for config file in PyInstaller executable directory (#682)
    _default_configs.append(os.path.join(
        os.path.dirname(sys.executable),
        "gallery-dl.conf",
    ))


# --------------------------------------------------------------------
# public interface


def initialize():
    paths = list(map(util.expand_path, _default_configs))

    for path in paths:
        if os.access(path, os.R_OK | os.W_OK):
            log.error("There is already a configuration file at '%s'", path)
            return 1

    for path in paths:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "x", encoding="utf-8") as fp:
                fp.write("""\
{
    "extractor": {

    },
    "downloader": {

    },
    "output": {

    },
    "postprocessor": {

    }
}
""")
            break
        except OSError as exc:
            log.debug("%s: %s", exc.__class__.__name__, exc)
    else:
        log.error("Unable to create a new configuration file "
                  "at any of the default paths")
        return 1

    log.info("Created a basic configuration file at '%s'", path)
    return 0


def open_extern():
    for path in _default_configs:
        path = util.expand_path(path)
        if os.access(path, os.R_OK | os.W_OK):
            break
    else:
        log.warning("Unable to find any writable configuration file")
        return 1

    if util.WINDOWS:
        openers = ("explorer", "notepad")
    else:
        openers = ("xdg-open", "open")
        if editor := os.environ.get("EDITOR"):
            openers = (editor,) + openers

    import shutil
    for opener in openers:
        if opener := shutil.which(opener):
            break
    else:
        log.warning("Unable to find a program to open '%s' with", path)
        return 1

    log.info("Running '%s %s'", opener, path)
    retcode = util.Popen((opener, path)).wait()

    if not retcode:
        try:
            with open(path, encoding="utf-8") as fp:
                util.json_loads(fp.read())
        except Exception as exc:
            log.warning("%s when parsing '%s': %s",
                        exc.__class__.__name__, path, exc)
            return 2

    return retcode


def status():
    from .output import stdout_write

    paths = []
    for path in _default_configs:
        path = util.expand_path(path)

        try:
            with open(path, encoding="utf-8") as fp:
                util.json_loads(fp.read())
        except FileNotFoundError:
            status = "Not Present"
        except OSError:
            status = "Inaccessible"
        except ValueError:
            status = "Invalid JSON"
        except Exception as exc:
            log.debug(exc)
            status = "Unknown"
        else:
            status = "OK"

        paths.append((path, status))

    fmt = f"{{:<{max(len(p[0]) for p in paths)}}} : {{}}\n".format

    for path, status in paths:
        stdout_write(fmt(path, status))


def remap_categories():
    opts = _config.get("extractor")
    if not opts:
        return

    cmap = opts.get("config-map")
    if cmap is None:
        cmap = (
            ("coomerparty" , "coomer"),
            ("kemonoparty" , "kemono"),
            ("giantessbooru", "sizebooru"),
            ("koharu"      , "schalenetwork"),
            ("naver"       , "naver-blog"),
            ("chzzk"       , "naver-chzzk"),
            ("naverwebtoon", "naver-webtoon"),
            ("pixiv"       , "pixiv-novel"),
        )
    elif not cmap:
        return
    elif isinstance(cmap, dict):
        cmap = cmap.items()

    for old, new in cmap:
        if old in opts and new not in opts:
            opts[new] = opts[old]


def load(files=None, strict=False, loads=util.json_loads, conf=_config):
    """Load JSON configuration files"""
    for pathfmt in files or _default_configs:
        path = util.expand_path(pathfmt)
        try:
            with open(path, encoding="utf-8") as fp:
                config = loads(fp.read())
        except OSError as exc:
            if strict:
                log.error(exc)
                raise SystemExit(1)
        except Exception as exc:
            log.error("%s when loading '%s': %s",
                      exc.__class__.__name__, path, exc)
            if strict:
                raise SystemExit(2)
        else:
            if not conf:
                conf.update(config)
            else:
                util.combine_dict(conf, config)
            _files.append(pathfmt)

            if "subconfigs" in config:
                if subconfigs := config["subconfigs"]:
                    if isinstance(subconfigs, str):
                        subconfigs = (subconfigs,)
                    load(subconfigs, strict, loads, conf)


def clear():
    """Reset configuration to an empty state"""
    _config.clear()


def get(path, key, default=None, conf=_config):
    """Get the value of property 'key' or a default value"""
    try:
        for p in path:
            conf = conf[p]
        return conf[key]
    except Exception:
        return default


def interpolate(path, key, default=None, conf=_config):
    """Interpolate the value of 'key'"""
    if key in conf:
        return conf[key]
    try:
        for p in path:
            conf = conf[p]
            if key in conf:
                default = conf[key]
    except Exception:
        pass
    return default


def interpolate_common(common, paths, key, default=None, conf=_config):
    """Interpolate the value of 'key'
    using multiple 'paths' along a 'common' ancestor
    """
    if key in conf:
        return conf[key]

    # follow the common path
    try:
        for p in common:
            conf = conf[p]
            if key in conf:
                default = conf[key]
    except Exception:
        return default

    # try all paths until a value is found
    value = util.SENTINEL
    for path in paths:
        c = conf
        try:
            for p in path:
                c = c[p]
                if key in c:
                    value = c[key]
        except Exception:
            pass
        if value is not util.SENTINEL:
            return value
    return default


def accumulate(path, key, conf=_config):
    """Accumulate the values of 'key' along 'path'"""
    result = []
    try:
        if key in conf:
            if value := conf[key]:
                if isinstance(value, list):
                    result.extend(value)
                else:
                    result.append(value)
        for p in path:
            conf = conf[p]
            if key in conf:
                if value := conf[key]:
                    if isinstance(value, list):
                        result[:0] = value
                    else:
                        result.insert(0, value)
    except Exception:
        pass
    return result


def set(path, key, value, conf=_config):
    """Set the value of property 'key' for this session"""
    for p in path:
        try:
            conf = conf[p]
        except KeyError:
            conf[p] = conf = {}
    conf[key] = value


def setdefault(path, key, value, conf=_config):
    """Set the value of property 'key' if it doesn't exist"""
    for p in path:
        try:
            conf = conf[p]
        except KeyError:
            conf[p] = conf = {}
    return conf.setdefault(key, value)


def unset(path, key, conf=_config):
    """Unset the value of property 'key'"""
    try:
        for p in path:
            conf = conf[p]
        del conf[key]
    except Exception:
        pass


class apply():
    """Context Manager: apply a collection of key-value pairs"""

    def __init__(self, kvlist):
        self.original = []
        self.kvlist = kvlist

    def __enter__(self):
        for path, key, value in self.kvlist:
            self.original.append((path, key, get(path, key, util.SENTINEL)))
            set(path, key, value)

    def __exit__(self, exc_type, exc_value, traceback):
        self.original.reverse()
        for path, key, value in self.original:
            if value is util.SENTINEL:
                unset(path, key)
            else:
                set(path, key, value)
