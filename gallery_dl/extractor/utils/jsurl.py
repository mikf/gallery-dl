# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.


def parse(data):
    """Parse JSURL data

    Nested lists and dicts are handled in a special way to deal
    with the way Tsumino expects its parameters -> expand(...)

    Example: ~(name~'John*20Doe~age~42~children~(~'Mary~'Bill))
    Ref: https://github.com/Sage/jsurl
    """
    i = 0
    imax = len(data)

    def eat(expected):
        nonlocal i

        if data[i] != expected:
            raise ValueError(
                f"bad JSURL syntax: expected '{expected}', got {data[i]}")
        i += 1

    def decode():
        nonlocal i

        beg = i
        result = ""

        while i < imax:
            ch = data[i]

            if ch not in "~)*!":
                i += 1

            elif ch == "*":
                if beg < i:
                    result += data[beg:i]
                if data[i + 1] == "*":
                    result += chr(int(data[i+2:i+6], 16))
                    i += 6
                else:
                    result += chr(int(data[i+1:i+3], 16))
                    i += 3
                beg = i

            elif ch == "!":
                if beg < i:
                    result += data[beg:i]
                result += "$"
                i += 1
                beg = i

            else:
                break

        return result + data[beg:i]

    def parse_one():
        nonlocal i

        eat('~')
        result = ""
        ch = data[i]

        if ch == "(":
            i += 1

            if data[i] == "~":
                result = []
                if data[i+1] == ")":
                    i += 1
                else:
                    result.append(parse_one())
                    while data[i] == "~":
                        result.append(parse_one())

            else:
                result = {}

                if data[i] != ")":
                    while True:
                        key = decode()
                        value = parse_one()
                        for ekey, evalue in expand(key, value):
                            result[ekey] = evalue
                        if data[i] != "~":
                            break
                        i += 1
            eat(")")

        elif ch == "'":
            i += 1
            result = decode()

        else:
            beg = i
            i += 1

            while i < imax and data[i] not in "~)":
                i += 1

            sub = data[beg:i]
            if ch in "0123456789-":
                fval = float(sub)
                ival = int(fval)
                result = ival if ival == fval else fval
            else:
                if sub not in ("true", "false", "null"):
                    raise ValueError("bad value keyword: " + sub)
                result = sub

        return result

    def expand(key, value):
        if isinstance(value, list):
            for index, cvalue in enumerate(value):
                ckey = f"{key}[{index}]"
                yield from expand(ckey, cvalue)
        elif isinstance(value, dict):
            for ckey, cvalue in value.items():
                ckey = f"{key}[{ckey}]"
                yield from expand(ckey, cvalue)
        else:
            yield key, value

    return parse_one()
