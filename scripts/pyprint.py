#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2024-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.


def pyprint(obj, indent=0, sort=None, oneline=True, lmin=0, lmax=16):

    if isinstance(obj, str):
        if obj.startswith("lit:"):
            return f'''{obj[4:]}'''

        if "\\" in obj or obj.startswith("re:"):
            prefix = "r"
        else:
            prefix = ""

        quote_beg = quote_end = '"'
        if "\n" in obj:
            quote_beg = '"""\\\n'
            quote_end = '\\\n"""'
        elif '"' in obj:
            quote_beg = quote_end = \
                "'''" if obj[0] == '"' or obj[-1] == '"' else '"""'

        return f'''{prefix}{quote_beg}{obj}{quote_end}'''

    if isinstance(obj, bytes):
        return f'''b"{str(obj)[2:-1]}"'''

    if isinstance(obj, type):
        if obj.__module__ == "builtins":
            return f'''{obj.__name__}'''

        name = obj.__module__.rpartition(".")[2]
        if name[0].isdecimal():
            name = f"_{name}"
        return f'''{name}.{obj.__name__}'''

    if isinstance(obj, dict):
        if not obj:
            return "{}"
        if len(obj) == 1 and oneline:
            key, value = next(iter(obj.items()))
            return f'''{{"{key}": {pyprint(value, indent, sort)}}}'''

        if sort:
            if callable(sort):
                lst = [(sort(key, value), key, value)
                       for key, value in obj.items()]
                lst.sort()
                obj = {key: value for _, key, value in lst}
            else:
                keys = list(obj)
                keys.sort()
                obj = {key: obj[key] for key in keys}

        try:
            keylen = max(kl for kl in map(len, obj) if kl <= lmax)
        except Exception:
            keylen = lmin
        if keylen < lmin:
            keylen = lmin
        ws = " " * indent

        lines = ["{"]
        for key, value in obj.items():
            if key.startswith("#blank-"):
                lines.append("")
            else:
                lines.append(
                    f'''{ws}    "{key}"'''
                    f'''{' '*(keylen - len(key))}: '''
                    f'''{pyprint(value, indent+4, sort)},'''
                )
        lines.append(f'''{ws}}}''')
        return "\n".join(lines)

    if isinstance(obj, list):
        if not obj:
            return "[]"
        if len(obj) == 1 and oneline:
            return f'''[{pyprint(obj[0], indent, sort)}]'''

        ws = " " * indent
        lines = ["["]
        for value in obj:
            lines.append(f'''{ws}    {pyprint(value, indent+4, sort)},''')
        lines.append(f'''{ws}]''')
        return "\n".join(lines)

    if isinstance(obj, tuple):
        if not obj:
            return "()"
        if len(obj) == 1:
            return f'''({pyprint(obj[0], indent, sort)},)'''

        result = f'''({", ".join(pyprint(v, indent+4, sort) for v in obj)})'''
        if len(result) < 80:
            return result

        ws = " " * indent
        lines = ["("]
        for value in obj:
            lines.append(f'''{ws}    {pyprint(value, indent+4, sort)},''')
        lines.append(f'''{ws})''')
        return "\n".join(lines)

    if isinstance(obj, set):
        if not obj:
            return "set()"
        return f'''{{{", ".join(pyprint(v, indent+4, sort) for v in obj)}}}'''

    if obj.__class__.__name__ == "datetime":
        if (off := obj.utcoffset()) is not None:
            obj = obj.replace(tzinfo=None, microsecond=0) - off
        elif obj.microsecond:
            obj = obj.replace(microsecond=0)
        return f'''"dt:{obj}"'''

    return f'''{obj}'''
