# -*- coding: utf-8 -*-

# Copyright 2018-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Common classes and constants used by postprocessor modules."""

from .. import util, formatter


class PostProcessor():
    """Base class for postprocessors"""

    def __init__(self, job):
        self.name = self.__class__.__name__[:-2].lower()
        self.log = job.get_logger("postprocessor." + self.name)

    def __repr__(self):
        return self.__class__.__name__

    def _init_archive(self, job, options, prefix=None):
        archive = options.get("archive")
        if archive:
            extr = job.extractor
            archive = util.expand_path(archive)
            if not prefix:
                prefix = "_" + self.name.upper() + "_"
            archive_format = (
                options.get("archive-prefix", extr.category) +
                options.get("archive-format", prefix + extr.archive_fmt))
            try:
                if "{" in archive:
                    archive = formatter.parse(archive).format_map(
                        job.pathfmt.kwdict)
                self.archive = util.DownloadArchive(
                    archive, archive_format,
                    options.get("archive-pragma"),
                    "_archive_" + self.name)
            except Exception as exc:
                self.log.warning(
                    "Failed to open %s archive at '%s' ('%s: %s')",
                    self.name, archive, exc.__class__.__name__, exc)
            else:
                self.log.debug("Using %s archive '%s'", self.name, archive)
        else:
            self.archive = None
