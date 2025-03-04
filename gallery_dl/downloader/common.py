# -*- coding: utf-8 -*-

# Copyright 2014-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Common classes and constants used by downloader modules."""

import os
from .. import config, util
_config = config._config


class DownloaderBase():
    """Base class for downloaders"""
    scheme = ""

    def __init__(self, job):
        extractor = job.extractor
        self.log = job.get_logger("downloader." + self.scheme)

        opts = self._extractor_config(extractor)
        if opts:
            self.opts = opts
            self.config = self.config_opts

        self.out = job.out
        self.session = extractor.session
        self.part = self.config("part", True)
        self.partdir = self.config("part-directory")

        if self.partdir:
            self.partdir = util.expand_path(self.partdir)
            os.makedirs(self.partdir, exist_ok=True)

        proxies = self.config("proxy", util.SENTINEL)
        if proxies is util.SENTINEL:
            self.proxies = extractor._proxies
        else:
            self.proxies = util.build_proxy_map(proxies, self.log)

    def config(self, key, default=None):
        """Interpolate downloader config value for 'key'"""
        return config.interpolate(("downloader", self.scheme), key, default)

    def config_opts(self, key, default=None, conf=_config):
        if key in conf:
            return conf[key]
        value = self.opts.get(key, util.SENTINEL)
        if value is not util.SENTINEL:
            return value
        return config.interpolate(("downloader", self.scheme), key, default)

    def _extractor_config(self, extractor):
        path = extractor._cfgpath
        if not isinstance(path, list):
            return self._extractor_opts(path[1], path[2])

        opts = {}
        for cat, sub in reversed(path):
            popts = self._extractor_opts(cat, sub)
            if popts:
                opts.update(popts)
        return opts

    def _extractor_opts(self, category, subcategory):
        cfg = config.get(("extractor",), category)
        if not cfg:
            return None

        copts = cfg.get(self.scheme)
        if copts:
            if subcategory in cfg:
                try:
                    sopts = cfg[subcategory].get(self.scheme)
                    if sopts:
                        opts = copts.copy()
                        opts.update(sopts)
                        return opts
                except Exception:
                    self._report_config_error(subcategory, cfg[subcategory])
            return copts

        if subcategory in cfg:
            try:
                return cfg[subcategory].get(self.scheme)
            except Exception:
                self._report_config_error(subcategory, cfg[subcategory])

        return None

    def _report_config_error(self, subcategory, value):
        config.log.warning("Subcategory '%s' set to '%s' instead of object",
                           subcategory, util.json_dumps(value).strip('"'))

    def download(self, url, pathfmt):
        """Write data from 'url' into the file specified by 'pathfmt'"""
