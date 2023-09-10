#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import re
import sys
import itertools
import collections

import util
from gallery_dl import extractor


FORMAT = '''\
# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

{imports}


__tests__ = (
{tests}\
)
'''


def pprint(obj, indent=0, lmin=9, lmax=16):

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
                        f'''{pprint(value, indent+4)},'''
                    )
            lines.append(f'''{ws}}}''')
            return "\n".join(lines)
        else:
            key, value = obj.popitem()
            return f'''{{"{key}": {pprint(value)}}}'''

    if isinstance(obj, list):
        if not obj:
            return "[]"

        if len(obj) >= 2:
            ws = " " * indent

            lines = []
            lines.append("[")
            lines.extend(
                f'''{ws}    {pprint(value, indent+4)},'''
                for value in obj
            )
            lines.append(f'''{ws}]''')
            return "\n".join(lines)
        else:
            return f'''[{pprint(obj[0])}]'''

    if isinstance(obj, tuple):
        if len(obj) == 1:
            return f'''({pprint(obj[0], indent+4)},)'''
        return f'''({", ".join(pprint(v, indent+4) for v in obj)})'''

    else:
        return f'''{obj}'''


def extract_tests_from_source(lines):
    tests = {}

    match_url = re.compile(
        r'''    (?:test = |    )?\(\(?"([^"]+)"(.*)''').match
    match_end = re.compile(
        r"    (\}\)|    \}\),)\n$").match
    first = 0
    url = ""

    for index, line in enumerate(lines):
        if first and match_end(line):
            tests[url] = lines[first-1:index+1]
            first = 0

        elif (m := match_url(line)):
            offset = index
            while not m[2]:
                offset += 1
                next = lines[offset]
                line = line[:-2] + next[next.index('"')+1:]
                m = match_url(line)
            url = m[1]
            if m[2] in (",)", "),"):
                tests[url] = lines[index-1:index+1]
                first = 0
            else:
                first = index

    return tests


def get_test_source(extr, *, cache={}):
    try:
        tests = cache[extr.__module__]
    except KeyError:
        path = sys.modules[extr.__module__].__file__
        with open(path) as fp:
            lines = fp.readlines()
        tests = cache[extr.__module__] = extract_tests_from_source(lines)
    return tests.get(extr.url) or ("",)
    return tests[extr.url]


def comment_from_source(source):
    match = re.match(r"\s+#\s*(.+)", source[0])
    return match[1] if match else ""


def build_test(extr, data):
    source = get_test_source(extr)
    comment = comment_from_source(source)

    head = {
        "#url"     : extr.url,
        "#comment" : comment.replace('"', "'"),
        "#category": (extr.basecategory,
                      extr.category,
                      extr.subcategory),
        "#class"   : extr.__class__,
    }

    if not comment:
        del head["#comment"]

    instr = {}

    if not data:
        data = {}
    if (options := data.pop("options", None)):
        instr["#options"] = {
            name: value
            for name, value in options
        }
    if (pattern := data.pop("pattern", None)):
        if pattern in PATTERNS:
            cls = PATTERNS[pattern]
            pattern = f"lit:{pprint(cls)}.pattern"
        instr["#pattern"] = pattern
    if (exception := data.pop("exception", None)):
        instr["#exception"] = exception
    if (range := data.pop("range", None)):
        instr["#range"] = range
    if (count := data.pop("count", None)) is not None:
        instr["#count"] = count
    if (archive := data.pop("archive", None)) is not None:
        instr["#archive"] = archive
    if (extractor := data.pop("extractor", None)) is not None:
        instr["#extractor"] = extractor
    if (url := data.pop("url", None)):
        instr["#sha1_url"] = url
    if (metadata := data.pop("keyword", None)):
        if isinstance(metadata, str) and len(metadata) == 40:
            instr["#sha1_metadata"] = metadata
            metadata = {}
    if (content := data.pop("content", None)):
        if isinstance(content, tuple):
            content = list(content)
        instr["#sha1_content"] = content

    if data:
        print(extr)
        for k in data:
            print(k)
        exit()

    return head, instr, metadata


def collect_patterns():
    return {
        cls.pattern.pattern: cls
        for cls in extractor._list_classes()
    }


def collect_tests(whitelist=None):
    tests = collections.defaultdict(list)

    for cls in extractor._list_classes():
        for url, data in cls._get_tests():

            extr = cls.from_url(url)
            if whitelist and extr.category not in whitelist:
                continue
            test = build_test(extr, data)
            tests[extr.category].append(test)

    return tests


def export_tests(data):
    imports = {}
    tests = []

    for head, instr, metadata in data:

        for v in itertools.chain(
            head.values(),
            instr.values() if instr else (),
            metadata.values() if metadata else (),
        ):
            if not isinstance(v, type) or v.__module__ == "builtins":
                continue

            module, _, name = v.__module__.rpartition(".")
            if name[0].isdecimal():
                stmt = f'''\
{module.partition(".")[0]} = __import__("{v.__module__}")
_{name} = getattr({module}, "{name}")'''
            elif module:
                stmt = f"from {module} import {name}"
            else:
                stmt = f"import {name}"
            imports[v.__module__] = stmt

        test = pprint(head)
        if instr:
            test = f"{test[:-2]}{pprint(instr)[1:]}"
        if metadata:
            for k, v in metadata.items():
                if v == "type:datetime":
                    imports["datetime"] = "import datetime"
                    metadata[k] = "lit:datetime.datetime"
            test = f"{test[:-1]}{pprint(metadata, lmin=0)[1:]}"

        tests.append(f"{test},\n\n")

    return FORMAT.format(
        imports="\n".join(imports.values()),
        tests="".join(tests),
    )


PATTERNS = None
DIRECTORY = "/tmp/_/results"


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t", "--target",
        help="target directory",
    )
    parser.add_argument(
        "-c", "--category", action="append",
        help="extractor categories to export",
    )

    args = parser.parse_args()

    if not args.target:
        args.target = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "test", "results",
        )

    global PATTERNS
    PATTERNS = collect_patterns()

    os.makedirs(args.target, exist_ok=True)
    for name, tests in collect_tests(args.category).items():
        name = name.replace(".", "")
        with util.lazy(f"{args.target}/{name}.py") as file:
            file.write(export_tests(tests))


if __name__ == "__main__":
    main()
