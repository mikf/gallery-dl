# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Write metadata to external files"""

from .common import PostProcessor
from .. import util, formatter
import json
import sys
import os


class MetadataPP(PostProcessor):

    def __init__(self, job, options):
        PostProcessor.__init__(self, job)

        mode = options.get("mode")
        cfmt = options.get("content-format") or options.get("format")
        omode = "w"
        filename = None

        if mode == "tags":
            self.write = self._write_tags
            ext = "txt"
        elif mode == "modify":
            self.run = self._run_modify
            self.fields = {
                name: formatter.parse(value, None, util.identity).format_map
                for name, value in options.get("fields").items()
            }
            ext = None
        elif mode == "delete":
            self.run = self._run_delete
            self.fields = options.get("fields")
            ext = None
        elif mode == "custom" or not mode and cfmt:
            self.write = self._write_custom
            if isinstance(cfmt, list):
                cfmt = "\n".join(cfmt) + "\n"
            self._content_fmt = formatter.parse(cfmt).format_map
            ext = "txt"
        elif mode == "jsonl":
            self.write = self._write_json
            self._json_encode = self._make_encoder(options).encode
            omode = "a"
            filename = "data.jsonl"
        else:
            self.write = self._write_json
            self._json_encode = self._make_encoder(options, 4).encode
            ext = "json"

        base_directory = options.get("base-directory")
        if base_directory:
            if base_directory is True:
                self._base = lambda p: p.basedirectory
            else:
                sep = os.sep
                altsep = os.altsep
                base_directory = util.expand_path(base_directory)
                if altsep and altsep in base_directory:
                    base_directory = base_directory.replace(altsep, sep)
                if base_directory[-1] != sep:
                    base_directory += sep
                self._base = lambda p: base_directory

        directory = options.get("directory")
        if isinstance(directory, list):
            self._directory = self._directory_format
            self._directory_formatters = [
                formatter.parse(dirfmt, util.NONE).format_map
                for dirfmt in directory
            ]
        elif directory:
            self._directory = self._directory_custom
            sep = os.sep + (os.altsep or "")
            self._metadir = util.expand_path(directory).rstrip(sep) + os.sep

        filename = options.get("filename", filename)
        extfmt = options.get("extension-format")
        if filename:
            if filename == "-":
                self.run = self._run_stdout
            else:
                self._filename = self._filename_custom
                self._filename_fmt = formatter.parse(filename).format_map
        elif extfmt:
            self._filename = self._filename_extfmt
            self._extension_fmt = formatter.parse(extfmt).format_map
        else:
            self.extension = options.get("extension", ext)

        events = options.get("event")
        if events is None:
            events = ("file",)
        elif isinstance(events, str):
            events = events.split(",")
        job.register_hooks({event: self.run for event in events}, options)

        self._init_archive(job, options, "_MD_")
        self.filter = self._make_filter(options)
        self.mtime = options.get("mtime")
        self.omode = options.get("open", omode)
        self.encoding = options.get("encoding", "utf-8")
        self.skip = options.get("skip", False)
        self.meta_path = options.get("metadata-path")

    def run(self, pathfmt):
        archive = self.archive
        if archive and archive.check(pathfmt.kwdict):
            return

        if util.WINDOWS and pathfmt.extended:
            directory = pathfmt._extended_path(self._directory(pathfmt))
        else:
            directory = self._directory(pathfmt)
        path = directory + self._filename(pathfmt)

        if self.meta_path is not None:
            pathfmt.kwdict[self.meta_path] = path

        if self.skip and os.path.exists(path):
            return

        try:
            with open(path, self.omode, encoding=self.encoding) as fp:
                self.write(fp, pathfmt.kwdict)
        except FileNotFoundError:
            os.makedirs(directory, exist_ok=True)
            with open(path, self.omode, encoding=self.encoding) as fp:
                self.write(fp, pathfmt.kwdict)

        if archive:
            archive.add(pathfmt.kwdict)

        if self.mtime:
            mtime = pathfmt.kwdict.get("_mtime")
            if mtime:
                util.set_mtime(path, mtime)

    def _run_stdout(self, pathfmt):
        self.write(sys.stdout, pathfmt.kwdict)

    def _run_modify(self, pathfmt):
        kwdict = pathfmt.kwdict
        for key, func in self.fields.items():
            obj = kwdict
            try:
                if "[" in key:
                    obj, key = _traverse(obj, key)
                obj[key] = func(kwdict)
            except Exception:
                pass

    def _run_delete(self, pathfmt):
        kwdict = pathfmt.kwdict
        for key in self.fields:
            obj = kwdict
            try:
                if "[" in key:
                    obj, key = _traverse(obj, key)
                del obj[key]
            except Exception:
                pass

    def _base(self, pathfmt):
        return pathfmt.realdirectory

    def _directory(self, pathfmt):
        return self._base(pathfmt)

    def _directory_custom(self, pathfmt):
        return os.path.join(self._base(pathfmt), self._metadir)

    def _directory_format(self, pathfmt):
        formatters = pathfmt.directory_formatters
        conditions = pathfmt.directory_conditions
        try:
            pathfmt.directory_formatters = self._directory_formatters
            pathfmt.directory_conditions = ()
            segments = pathfmt.build_directory(pathfmt.kwdict)
            if segments:
                directory = pathfmt.clean_path(os.sep.join(segments) + os.sep)
            else:
                directory = "." + os.sep
            return os.path.join(self._base(pathfmt), directory)
        finally:
            pathfmt.directory_conditions = conditions
            pathfmt.directory_formatters = formatters

    def _filename(self, pathfmt):
        return (pathfmt.filename or "metadata") + "." + self.extension

    def _filename_custom(self, pathfmt):
        return pathfmt.clean_path(pathfmt.clean_segment(
            self._filename_fmt(pathfmt.kwdict)))

    def _filename_extfmt(self, pathfmt):
        kwdict = pathfmt.kwdict
        ext = kwdict.get("extension")
        kwdict["extension"] = pathfmt.extension
        kwdict["extension"] = pathfmt.prefix + self._extension_fmt(kwdict)
        filename = pathfmt.build_filename(kwdict)
        kwdict["extension"] = ext
        return filename

    def _write_custom(self, fp, kwdict):
        fp.write(self._content_fmt(kwdict))

    def _write_tags(self, fp, kwdict):
        tags = kwdict.get("tags") or kwdict.get("tag_string")

        if not tags:
            return

        if isinstance(tags, str):
            taglist = tags.split(", ")
            if len(taglist) < len(tags) / 16:
                taglist = tags.split(" ")
            tags = taglist
        elif isinstance(tags, dict):
            taglists = tags.values()
            tags = []
            extend = tags.extend
            for taglist in taglists:
                extend(taglist)
            tags.sort()
        elif all(isinstance(e, dict) for e in tags):
            taglists = tags
            tags = []
            extend = tags.extend
            for tagdict in taglists:
                extend([x for x in tagdict.values() if isinstance(x, str)])
            tags.sort()

        fp.write("\n".join(tags) + "\n")

    def _write_json(self, fp, kwdict):
        if self.filter:
            kwdict = self.filter(kwdict)
        fp.write(self._json_encode(kwdict) + "\n")

    def _make_filter(self, options):
        include = options.get("include")
        if include:
            if isinstance(include, str):
                include = include.split(",")
            return lambda d: {k: d[k] for k in include if k in d}

        exclude = options.get("exclude")
        private = options.get("private")
        if exclude:
            if isinstance(exclude, str):
                exclude = exclude.split(",")
            exclude = set(exclude)

            if private:
                return lambda d: {k: v for k, v in d.items()
                                  if k not in exclude}
            return lambda d: {k: v for k, v in util.filter_dict(d).items()
                              if k not in exclude}

        if not private:
            return util.filter_dict

    @staticmethod
    def _make_encoder(options, indent=None):
        return json.JSONEncoder(
            ensure_ascii=options.get("ascii", False),
            sort_keys=options.get("sort", False),
            separators=options.get("separators"),
            indent=options.get("indent", indent),
            check_circular=False,
            default=util.json_default,
        )


def _traverse(obj, key):
    name, _, key = key.partition("[")
    obj = obj[name]

    while "[" in key:
        name, _, key = key.partition("[")
        obj = obj[name.strip("\"']")]

    return obj, key.strip("\"']")


__postprocessor__ = MetadataPP
