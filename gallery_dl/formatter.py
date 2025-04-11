# -*- coding: utf-8 -*-

# Copyright 2021-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""String formatters"""

import os
import sys
import time
import string
import _string
import datetime
import operator
from . import text, util

NONE = util.NONE


def parse(format_string, default=NONE, fmt=format):
    key = format_string, default, fmt

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
        elif kind == "TF":
            cls = TemplateFStringFormatter
        elif kind == "E":
            cls = ExpressionFormatter
        elif kind == "M":
            cls = ModuleFormatter
        elif kind == "F":
            cls = FStringFormatter

    formatter = _CACHE[key] = cls(format_string, default, fmt)
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
    - "g": calls text.slugify()
    - "j": calls json.dumps
    - "t": calls str.strip
    - "T": calls util.datetime_to_timestamp_string()
    - "d": calls text.parse_timestamp
    - "s": calls str()
    - "S": calls util.to_string()
    - "U": calls urllib.parse.unescape
    - "r": calls repr()
    - "a": calls ascii()
    - Example: {f!l} -> "example"; {f!u} -> "EXAMPLE"

    # Go to _CONVERSIONS and _SPECIFIERS below to se all of them, read:
    # https://github.com/mikf/gallery-dl/blob/master/docs/formatting.md

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

    def __init__(self, format_string, default=NONE, fmt=format):
        self.default = default
        self.format = fmt
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
        fmt = self._parse_format_spec(format_spec, conversion)

        if "|" in field_name:
            return self._apply_list([
                parse_field_name(fn)
                for fn in field_name.split("|")
            ], fmt)
        else:
            key, funcs = parse_field_name(field_name)
            if key in _GLOBALS:
                return self._apply_globals(_GLOBALS[key], funcs, fmt)
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

    def _apply_globals(self, gobj, funcs, fmt):
        def wrap(_):
            try:
                obj = gobj()
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
                    obj = _GLOBALS[key]() if key in _GLOBALS else kwdict[key]
                    for func in funcs:
                        obj = func(obj)
                    if obj:
                        break
                except Exception:
                    obj = None
            else:
                if obj is None:
                    obj = self.default
            return fmt(obj)
        return wrap

    def _parse_format_spec(self, format_spec, conversion):
        fmt = _build_format_func(format_spec, self.format)
        if not conversion:
            return fmt

        conversion = _CONVERSIONS[conversion]
        if fmt is self.format:
            return conversion
        else:
            return lambda obj: fmt(conversion(obj))


class ExpressionFormatter():
    """Generate text by evaluating a Python expression"""

    def __init__(self, expression, default=NONE, fmt=None):
        self.format_map = util.compile_expression(expression)


class ModuleFormatter():
    """Generate text by calling an external function"""

    def __init__(self, function_spec, default=NONE, fmt=None):
        module_name, _, function_name = function_spec.rpartition(":")
        module = util.import_file(module_name)
        self.format_map = getattr(module, function_name)


class FStringFormatter():
    """Generate text by evaluating an f-string literal"""

    def __init__(self, fstring, default=NONE, fmt=None):
        self.format_map = util.compile_expression('f"""' + fstring + '"""')


class TemplateFormatter(StringFormatter):
    """Read format_string from file"""

    def __init__(self, path, default=NONE, fmt=format):
        with open(util.expand_path(path)) as fp:
            format_string = fp.read()
        StringFormatter.__init__(self, format_string, default, fmt)


class TemplateFStringFormatter(FStringFormatter):
    """Read f-string from file"""

    def __init__(self, path, default=NONE, fmt=None):
        with open(util.expand_path(path)) as fp:
            fstring = fp.read()
        FStringFormatter.__init__(self, fstring, default, fmt)


def parse_field_name(field_name):
    if field_name[0] == "'":
        return "_lit", (operator.itemgetter(field_name[1:-1]),)

    first, rest = _string.formatter_field_name_split(field_name)
    funcs = []

    for is_attr, key in rest:
        if is_attr:
            func = operator.attrgetter
        else:
            func = operator.itemgetter
            try:
                if ":" in key:
                    if key[0] == "b":
                        func = _bytesgetter
                        key = _slice(key[1:])
                    else:
                        key = _slice(key)
                else:
                    key = key.strip("\"'")
            except TypeError:
                pass  # key is an integer

        funcs.append(func(key))

    return first, funcs


def _slice(indices):
    start, _, stop = indices.partition(":")
    stop, _, step = stop.partition(":")
    return slice(
        int(start) if start else None,
        int(stop) if stop else None,
        int(step) if step else None,
    )


def _bytesgetter(slice, encoding=sys.getfilesystemencoding()):

    def apply_slice_bytes(obj):
        return obj.encode(encoding)[slice].decode(encoding, "ignore")

    return apply_slice_bytes


def _build_format_func(format_spec, default):
    if format_spec:
        return _FORMAT_SPECIFIERS.get(
            format_spec[0], _default_format)(format_spec, default)
    return default


def _parse_optional(format_spec, default):
    before, after, format_spec = format_spec.split(_SEPARATOR, 2)
    before = before[1:]
    fmt = _build_format_func(format_spec, default)

    def optional(obj):
        return before + fmt(obj) + after if obj else ""
    return optional


def _parse_slice(format_spec, default):
    indices, _, format_spec = format_spec.partition("]")
    fmt = _build_format_func(format_spec, default)

    if indices[1] == "b":
        slice_bytes = _bytesgetter(_slice(indices[2:]))

        def apply_slice(obj):
            return fmt(slice_bytes(obj))

    else:
        slice = _slice(indices[1:])

        def apply_slice(obj):
            return fmt(obj[slice])

    return apply_slice


def _parse_arithmetic(format_spec, default):
    op, _, format_spec = format_spec.partition(_SEPARATOR)
    fmt = _build_format_func(format_spec, default)

    value = int(op[2:])
    op = op[1]

    if op == "+":
        return lambda obj: fmt(obj + value)
    if op == "-":
        return lambda obj: fmt(obj - value)
    if op == "*":
        return lambda obj: fmt(obj * value)

    return fmt


def _parse_conversion(format_spec, default):
    conversions, _, format_spec = format_spec.partition(_SEPARATOR)
    convs = [_CONVERSIONS[c] for c in conversions[1:]]
    fmt = _build_format_func(format_spec, default)

    if len(conversions) <= 2:

        def convert_one(obj):
            return fmt(conv(obj))
        conv = _CONVERSIONS[conversions[1]]
        return convert_one

    def convert_many(obj):
        for conv in convs:
            obj = conv(obj)
        return fmt(obj)
    convs = [_CONVERSIONS[c] for c in conversions[1:]]
    return convert_many


def _parse_maxlen(format_spec, default):
    maxlen, replacement, format_spec = format_spec.split(_SEPARATOR, 2)
    maxlen = text.parse_int(maxlen[1:])
    fmt = _build_format_func(format_spec, default)

    def mlen(obj):
        obj = fmt(obj)
        return obj if len(obj) <= maxlen else replacement
    return mlen


def _parse_join(format_spec, default):
    separator, _, format_spec = format_spec.partition(_SEPARATOR)
    join = separator[1:].join
    fmt = _build_format_func(format_spec, default)

    def apply_join(obj):
        if isinstance(obj, str):
            return fmt(obj)
        return fmt(join(obj))
    return apply_join


def _parse_replace(format_spec, default):
    old, new, format_spec = format_spec.split(_SEPARATOR, 2)
    old = old[1:]
    fmt = _build_format_func(format_spec, default)

    def replace(obj):
        return fmt(obj.replace(old, new))
    return replace


def _parse_datetime(format_spec, default):
    dt_format, _, format_spec = format_spec.partition(_SEPARATOR)
    dt_format = dt_format[1:]
    fmt = _build_format_func(format_spec, default)

    def dt(obj):
        return fmt(text.parse_datetime(obj, dt_format))
    return dt


def _parse_offset(format_spec, default):
    offset, _, format_spec = format_spec.partition(_SEPARATOR)
    offset = offset[1:]
    fmt = _build_format_func(format_spec, default)

    if not offset or offset == "local":
        def off(dt):
            local = time.localtime(util.datetime_to_timestamp(dt))
            return fmt(dt + datetime.timedelta(0, local.tm_gmtoff))
    else:
        hours, _, minutes = offset.partition(":")
        offset = 3600 * int(hours)
        if minutes:
            offset += 60 * (int(minutes) if offset > 0 else -int(minutes))
        offset = datetime.timedelta(0, offset)

        def off(obj):
            return fmt(obj + offset)
    return off


def _parse_sort(format_spec, default):
    args, _, format_spec = format_spec.partition(_SEPARATOR)
    fmt = _build_format_func(format_spec, default)

    if "d" in args or "r" in args:
        def sort_desc(obj):
            return fmt(sorted(obj, reverse=True))
        return sort_desc
    else:
        def sort_asc(obj):
            return fmt(sorted(obj))
        return sort_asc


def _parse_limit(format_spec, default):
    limit, hint, format_spec = format_spec.split(_SEPARATOR, 2)
    limit = int(limit[1:])
    limit_hint = limit - len(hint)
    fmt = _build_format_func(format_spec, default)

    def apply_limit(obj):
        if len(obj) > limit:
            obj = obj[:limit_hint] + hint
        return fmt(obj)
    return apply_limit


def _default_format(format_spec, default):
    def wrap(obj):
        return format(obj, format_spec)
    return wrap


class Literal():
    # __getattr__, __getattribute__, and __class_getitem__
    # are all slower than regular __getitem__

    @staticmethod
    def __getitem__(key):
        return key


_literal = Literal()

_CACHE = {}
_SEPARATOR = "/"
_GLOBALS = {
    "_env": lambda: os.environ,
    "_lit": lambda: _literal,
    "_now": datetime.datetime.now,
    "_nul": lambda: util.NONE,
}
_CONVERSIONS = {
    "l": str.lower,
    "u": str.upper,
    "c": str.capitalize,
    "C": string.capwords,
    "j": util.json_dumps,
    "t": str.strip,
    "L": len,
    "T": util.datetime_to_timestamp_string,
    "d": text.parse_timestamp,
    "U": text.unescape,
    "H": lambda s: text.unescape(text.remove_html(s)),
    "g": text.slugify,
    "S": util.to_string,
    "s": str,
    "r": repr,
    "a": ascii,
    "i": int,
    "f": float,
}
_FORMAT_SPECIFIERS = {
    "?": _parse_optional,
    "[": _parse_slice,
    "A": _parse_arithmetic,
    "C": _parse_conversion,
    "D": _parse_datetime,
    "J": _parse_join,
    "L": _parse_maxlen,
    "O": _parse_offset,
    "R": _parse_replace,
    "S": _parse_sort,
    "X": _parse_limit,
}
