#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2024-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import re


def pyprint(obj, indent=0, lmax=16):

    if isinstance(obj, str):
        if obj.startswith("lit:"):
            return f'''{obj[4:]}'''

        if "\\" in obj or obj.startswith("re:"):
            prefix = "r"
        else:
            prefix = ""

        if "\n" in obj:
            quote = '"""'
        elif '"' in obj:
            obj = re.sub(r'(?<!\\)"', '\\"', obj)
            quote = '"'
        else:
            quote = '"'

        return f'''{prefix}{quote}{obj}{quote}'''

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
        if len(obj) == 1:
            key, value = next(iter(obj.items()))
            return f'''{{"{key}": {pyprint(value, indent)}}}'''

        ws = " " * indent
        key_maxlen = max(kl for kl in map(len, obj) if kl <= lmax)

        lines = ["{"]
        for key, value in obj.items():
            if key.startswith("#blank-"):
                lines.append("")
            else:
                lines.append(
                    f'''{ws}    "{key}"'''
                    f'''{' '*(key_maxlen - len(key))}: '''
                    f'''{pyprint(value, indent+4)},'''
                )
        lines.append(f'''{ws}}}''')
        return "\n".join(lines)

    if isinstance(obj, list):
        if not obj:
            return "[]"
        if len(obj) == 1:
            return f'''[{pyprint(obj[0], indent)}]'''

        ws = " " * indent

        lines = ["{"]
        lines.extend(
            f'''{ws}    {pyprint(value, indent+4)},'''
            for value in obj
        )
        lines.append(f'''{ws}]''')
        return "\n".join(lines)

    if isinstance(obj, tuple):
        if not obj:
            return "()"
        if len(obj) == 1:
            return f'''({pyprint(obj[0])},)'''
        return f'''({", ".join(pyprint(v, indent+4) for v in obj)})'''

    if isinstance(obj, set):
        if not obj:
            return "set()"
        return f'''{{{", ".join(pyprint(v, indent+4) for v in obj)}}}'''

    if obj.__class__.__name__ == "datetime":
        if (off := obj.utcoffset()) is not None:
            obj = obj.replace(tzinfo=None, microsecond=0) - off
        elif obj.microsecond:
            obj = obj.replace(microsecond=0)
        return f'''"dt:{obj}"'''

    return f'''{obj}'''
