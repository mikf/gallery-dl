#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import re


def pyprint(obj, indent=0, lmin=9, lmax=16):

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

        if len(obj) >= 2 or not indent:
            ws = " " * indent

            lkey = max(map(len, obj))
            if not indent:
                if lkey < lmin:
                    lkey = lmin
                elif lkey > lmax:
                    lkey = lmax

            lines = []
            lines.append("{")
            for key, value in obj.items():
                if key.startswith("#blank-"):
                    lines.append("")
                else:
                    lines.append(
                        f'''{ws}    "{key}"'''
                        f'''{' '*(lkey - len(key))}: '''
                        f'''{pyprint(value, indent+4)},'''
                    )
            lines.append(f'''{ws}}}''')
            return "\n".join(lines)
        else:
            key, value = obj.popitem()
            return f'''{{"{key}": {pyprint(value)}}}'''

    if isinstance(obj, list):
        if not obj:
            return "[]"

        if len(obj) >= 2:
            ws = " " * indent

            lines = []
            lines.append("[")
            lines.extend(
                f'''{ws}    {pyprint(value, indent+4)},'''
                for value in obj
            )
            lines.append(f'''{ws}]''')
            return "\n".join(lines)
        else:
            return f'''[{pyprint(obj[0])}]'''

    if isinstance(obj, tuple):
        if len(obj) == 1:
            return f'''({pyprint(obj[0], indent+4)},)'''
        return f'''({", ".join(pyprint(v, indent+4) for v in obj)})'''

    else:
        return f'''{obj}'''
