# -*- coding: utf-8 -*-

# Copyright 2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""String formatters"""

import json
import string
import _string
import operator
from . import text, util

_CACHE = {}
_CONVERSIONS = None


def parse(format_string, default=None):
    key = format_string, default

    try:
        return _CACHE[key]
    except KeyError:
        pass

    cls = StringFormatter
    if format_string.startswith("\f"):
        kind, _, format_string = format_string.partition(" ")
        kind = kind[1:]

        if kind == "T":
            cls = TemplateFormatter
        elif kind == "E":
            cls = ExpressionFormatter
        elif kind == "M":
            cls = ModuleFormatter

    formatter = _CACHE[key] = cls(format_string, default)
    return formatter


class StringFormatter():
    """Custom, extended version of string.Formatter

    This string formatter implementation is a mostly performance-optimized
    variant of the original string.Formatter class. Unnecessary features have
    been removed (positional arguments, unused argument check) and new
    formatting options have been added.

    Extra Conversions:
    - "l": calls str.lower on the target value
    - "u": calls str.upper
    - "c": calls str.capitalize
    - "C": calls string.capwords
    - "j". calls json.dumps
    - "t": calls str.strip
    - "d": calls text.parse_timestamp
    - "U": calls urllib.parse.unquote
    - "S": calls util.to_string()
    - "T": calls util.to_timestamü()
    - Example: {f!l} -> "example"; {f!u} -> "EXAMPLE"

    Extra Format Specifiers:
    - "?<before>/<after>/":
        Adds <before> and <after> to the actual value if it evaluates to True.
        Otherwise the whole replacement field becomes an empty string.
        Example: {f:?-+/+-/} -> "-+Example+-" (if "f" contains "Example")
                             -> ""            (if "f" is None, 0, "")

    - "L<maxlen>/<replacement>/":
        Replaces the output with <replacement> if its length (in characters)
        exceeds <maxlen>. Otherwise everything is left as is.
        Example: {f:L5/too long/} -> "foo"      (if "f" is "foo")
                                  -> "too long" (if "f" is "foobar")

    - "J<separator>/":
        Joins elements of a list (or string) using <separator>
        Example: {f:J - /} -> "a - b - c" (if "f" is ["a", "b", "c"])

    - "R<old>/<new>/":
        Replaces all occurrences of <old> with <new>
        Example: {f:R /_/} -> "f_o_o_b_a_r" (if "f" is "f o o b a r")
    """

    def __init__(self, format_string, default=None):
        self.default = default
        self.result = []
        self.fields = []

        for literal_text, field_name, format_spec, conv in \
                _string.formatter_parser(format_string):
            if literal_text:
                self.result.append(literal_text)
            if field_name:
                self.fields.append((
                    len(self.result),
                    self._field_access(field_name, format_spec, conv),
                ))
                self.result.append("")

        if len(self.result) == 1:
            if self.fields:
                self.format_map = self.fields[0][1]
            else:
                self.format_map = lambda _: format_string
            del self.result, self.fields

    def format_map(self, kwdict):
        """Apply 'kwdict' to the initial format_string and return its result"""
        result = self.result
        for index, func in self.fields:
            result[index] = func(kwdict)
        return "".join(result)

    def _field_access(self, field_name, format_spec, conversion):
        fmt = parse_format_spec(format_spec, conversion)

        if "|" in field_name:
            return self._apply_list([
                parse_field_name(fn)
                for fn in field_name.split("|")
            ], fmt)
        else:
            key, funcs = parse_field_name(field_name)
            if funcs:
                return self._apply(key, funcs, fmt)
            return self._apply_simple(key, fmt)

    def _apply(self, key, funcs, fmt):
        def wrap(kwdict):
            try:
                obj = kwdict[key]
                for func in funcs:
                    obj = func(obj)
            except Exception:
                obj = self.default
            return fmt(obj)
        return wrap

    def _apply_simple(self, key, fmt):
        def wrap(kwdict):
            return fmt(kwdict[key] if key in kwdict else self.default)
        return wrap

    def _apply_list(self, lst, fmt):
        def wrap(kwdict):
            for key, funcs in lst:
                try:
                    obj = kwdict[key]
                    for func in funcs:
                        obj = func(obj)
                    if obj:
                        break
                except Exception:
                    pass
            else:
                obj = self.default
            return fmt(obj)
        return wrap


class TemplateFormatter(StringFormatter):
    """Read format_string from file"""

    def __init__(self, path, default=None):
        with open(util.expand_path(path)) as fp:
            format_string = fp.read()
        StringFormatter.__init__(self, format_string, default)


class ExpressionFormatter():
    """Generate text by evaluating a Python expression"""

    def __init__(self, expression, default=None):
        self.format_map = util.compile_expression(expression)


class ModuleFormatter():
    """Generate text by calling an external function"""

    def __init__(self, function_spec, default=None):
        module_name, _, function_name = function_spec.partition(":")
        module = __import__(module_name)
        self.format_map = getattr(module, function_name)


def parse_field_name(field_name):
    first, rest = _string.formatter_field_name_split(field_name)
    funcs = []

    for is_attr, key in rest:
        if is_attr:
            func = operator.attrgetter
        else:
            func = operator.itemgetter
            try:
                if ":" in key:
                    start, _, stop = key.partition(":")
                    stop, _, step = stop.partition(":")
                    start = int(start) if start else None
                    stop = int(stop) if stop else None
                    step = int(step) if step else None
                    key = slice(start, stop, step)
            except TypeError:
                pass  # key is an integer

        funcs.append(func(key))

    return first, funcs


def parse_format_spec(format_spec, conversion):
    fmt = build_format_func(format_spec)
    if not conversion:
        return fmt

    global _CONVERSIONS
    if _CONVERSIONS is None:
        _CONVERSIONS = {
            "l": str.lower,
            "u": str.upper,
            "c": str.capitalize,
            "C": string.capwords,
            "j": json.dumps,
            "t": str.strip,
            "T": util.to_timestamp,
            "d": text.parse_timestamp,
            "U": text.unescape,
            "S": util.to_string,
            "s": str,
            "r": repr,
            "a": ascii,
        }

    conversion = _CONVERSIONS[conversion]
    if fmt is format:
        return conversion
    else:
        def chain(obj):
            return fmt(conversion(obj))
        return chain


def build_format_func(format_spec):
    if format_spec:
        fmt = format_spec[0]
        if fmt == "?":
            return _parse_optional(format_spec)
        if fmt == "L":
            return _parse_maxlen(format_spec)
        if fmt == "J":
            return _parse_join(format_spec)
        if fmt == "R":
            return _parse_replace(format_spec)
        return _default_format(format_spec)
    return format


def _parse_optional(format_spec):
    before, after, format_spec = format_spec.split("/", 2)
    before = before[1:]
    fmt = build_format_func(format_spec)

    def optional(obj):
        return before + fmt(obj) + after if obj else ""
    return optional


def _parse_maxlen(format_spec):
    maxlen, replacement, format_spec = format_spec.split("/", 2)
    maxlen = text.parse_int(maxlen[1:])
    fmt = build_format_func(format_spec)

    def mlen(obj):
        obj = fmt(obj)
        return obj if len(obj) <= maxlen else replacement
    return mlen


def _parse_join(format_spec):
    separator, _, format_spec = format_spec.partition("/")
    separator = separator[1:]
    fmt = build_format_func(format_spec)

    def join(obj):
        return fmt(separator.join(obj))
    return join


def _parse_replace(format_spec):
    old, new, format_spec = format_spec.split("/", 2)
    old = old[1:]
    fmt = build_format_func(format_spec)

    def replace(obj):
        return fmt(obj.replace(old, new))
    return replace


def _default_format(format_spec):
    def wrap(obj):
        return format(obj, format_spec)
    return wrap
