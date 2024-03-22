#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import time
import unittest
import datetime
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gallery_dl import formatter, text, util  # noqa E402


class TestFormatter(unittest.TestCase):

    kwdict = {
        "a": "hElLo wOrLd",
        "b": "äöü",
        "j": "げんそうきょう",
        "d": {"a": "foo", "b": 0, "c": None},
        "l": ["a", "b", "c"],
        "n": None,
        "s": " \n\r\tSPACE    ",
        "h": "<p>foo </p> &amp; bar <p> </p>",
        "u": "&#x27;&lt; / &gt;&#x27;",
        "t": 1262304000,
        "ds": "2010-01-01T01:00:00+0100",
        "dt": datetime.datetime(2010, 1, 1),
        "dt_dst": datetime.datetime(2010, 6, 1),
        "name": "Name",
        "title1": "Title",
        "title2": "",
        "title3": None,
        "title4": 0,
    }

    def test_conversions(self):
        self._run_test("{a!l}", "hello world")
        self._run_test("{a!u}", "HELLO WORLD")
        self._run_test("{a!c}", "Hello world")
        self._run_test("{a!C}", "Hello World")
        self._run_test("{s!t}", "SPACE")
        self._run_test("{a!U}", self.kwdict["a"])
        self._run_test("{u!U}", "'< / >'")
        self._run_test("{a!H}", self.kwdict["a"])
        self._run_test("{h!H}", "foo & bar")
        self._run_test("{u!H}", "'< / >'")
        self._run_test("{n!H}", "")
        self._run_test("{a!s}", self.kwdict["a"])
        self._run_test("{a!r}", "'" + self.kwdict["a"] + "'")
        self._run_test("{a!a}", "'" + self.kwdict["a"] + "'")
        self._run_test("{b!a}", "'\\xe4\\xf6\\xfc'")
        self._run_test("{a!S}", self.kwdict["a"])
        self._run_test("{l!S}", "a, b, c")
        self._run_test("{n!S}", "")
        self._run_test("{t!d}", datetime.datetime(2010, 1, 1))
        self._run_test("{t!d:%Y-%m-%d}", "2010-01-01")
        self._run_test("{dt!T}", "1262304000")
        self._run_test("{l!j}", '["a", "b", "c"]')
        self._run_test("{dt!j}", '"2010-01-01 00:00:00"')
        self._run_test("{a!g}", "hello-world")

        with self.assertRaises(KeyError):
            self._run_test("{a!q}", "hello world")

    def test_optional(self):
        self._run_test("{name}{title1}", "NameTitle")
        self._run_test("{name}{title1:?//}", "NameTitle")
        self._run_test("{name}{title1:? **/''/}", "Name **Title''")

        self._run_test("{name}{title2}", "Name")
        self._run_test("{name}{title2:?//}", "Name")
        self._run_test("{name}{title2:? **/''/}", "Name")

        self._run_test("{name}{title3}", "NameNone")
        self._run_test("{name}{title3:?//}", "Name")
        self._run_test("{name}{title3:? **/''/}", "Name")

        self._run_test("{name}{title4}", "Name0")
        self._run_test("{name}{title4:?//}", "Name")
        self._run_test("{name}{title4:? **/''/}", "Name")

    def test_missing(self):
        replacement = "None"

        self._run_test("{missing}", replacement)
        self._run_test("{missing.attr}", replacement)
        self._run_test("{missing[key]}", replacement)
        self._run_test("{missing:?a//}", "")

        self._run_test("{name[missing]}", replacement)
        self._run_test("{name[missing].attr}", replacement)
        self._run_test("{name[missing][key]}", replacement)
        self._run_test("{name[missing]:?a//}", "")

    def test_missing_custom_default(self):
        replacement = default = "foobar"
        self._run_test("{missing}"     , replacement, default)
        self._run_test("{missing.attr}", replacement, default)
        self._run_test("{missing[key]}", replacement, default)
        self._run_test("{missing:?a//}", "a" + default, default)

    def test_fmt_func(self):
        self._run_test("{t}" , self.kwdict["t"] , None, int)
        self._run_test("{t}" , self.kwdict["t"] , None, util.identity)
        self._run_test("{dt}", self.kwdict["dt"], None, util.identity)
        self._run_test("{ds}", self.kwdict["dt"], None, text.parse_datetime)
        self._run_test("{ds:D%Y-%m-%dT%H:%M:%S%z}", self.kwdict["dt"],
                       None, util.identity)

    def test_alternative(self):
        self._run_test("{a|z}"    , "hElLo wOrLd")
        self._run_test("{z|a}"    , "hElLo wOrLd")
        self._run_test("{z|y|a}"  , "hElLo wOrLd")
        self._run_test("{z|y|x|a}", "hElLo wOrLd")
        self._run_test("{z|n|a|y}", "hElLo wOrLd")

        self._run_test("{z|a!C}"      , "Hello World")
        self._run_test("{z|a:Rh/C/}"  , "CElLo wOrLd")
        self._run_test("{z|a!C:RH/C/}", "Cello World")
        self._run_test("{z|y|x:?</>/}", "")

        self._run_test("{d[c]|d[b]|d[a]}", "foo")
        self._run_test("{d[a]|d[b]|d[c]}", "foo")
        self._run_test("{d[z]|d[y]|d[x]}", "None")

    def test_indexing(self):
        self._run_test("{l[0]}" , "a")
        self._run_test("{a[6]}" , "w")

    def test_dict_access(self):
        self._run_test("{d[a]}"  , "foo")
        self._run_test("{d['a']}", "foo")
        self._run_test('{d["a"]}', "foo")

    def test_slice_str(self):
        v = self.kwdict["a"]
        self._run_test("{a[1:10]}"  , v[1:10])
        self._run_test("{a[-10:-1]}", v[-10:-1])
        self._run_test("{a[5:]}" , v[5:])
        self._run_test("{a[50:]}", v[50:])
        self._run_test("{a[:5]}" , v[:5])
        self._run_test("{a[:50]}", v[:50])
        self._run_test("{a[:]}"  , v)
        self._run_test("{a[1:10:2]}"  , v[1:10:2])
        self._run_test("{a[-10:-1:2]}", v[-10:-1:2])
        self._run_test("{a[5::2]}" , v[5::2])
        self._run_test("{a[50::2]}", v[50::2])
        self._run_test("{a[:5:2]}" , v[:5:2])
        self._run_test("{a[:50:2]}", v[:50:2])
        self._run_test("{a[::]}"   , v)

        self._run_test("{a:[1:10]}"  , v[1:10])
        self._run_test("{a:[-10:-1]}", v[-10:-1])
        self._run_test("{a:[5:]}" , v[5:])
        self._run_test("{a:[50:]}", v[50:])
        self._run_test("{a:[:5]}" , v[:5])
        self._run_test("{a:[:50]}", v[:50])
        self._run_test("{a:[:]}"  , v)
        self._run_test("{a:[1:10:2]}"  , v[1:10:2])
        self._run_test("{a:[-10:-1:2]}", v[-10:-1:2])
        self._run_test("{a:[5::2]}" , v[5::2])
        self._run_test("{a:[50::2]}", v[50::2])
        self._run_test("{a:[:5:2]}" , v[:5:2])
        self._run_test("{a:[:50:2]}", v[:50:2])
        self._run_test("{a:[::]}"   , v)

    def test_slice_bytes(self):
        v = self.kwdict["j"]
        self._run_test("{j[b1:10]}"  , v[1:3])
        self._run_test("{j[b-10:-1]}", v[-3:-1])
        self._run_test("{j[b5:]}"    , v[2:])
        self._run_test("{j[b50:]}"   , v[50:])
        self._run_test("{j[b:5]}"    , v[:1])
        self._run_test("{j[b:50]}"   , v[:50])
        self._run_test("{j[b:]}"     , v)
        self._run_test("{j[b::]}"    , v)

        self._run_test("{j:[b1:10]}"  , v[1:3])
        self._run_test("{j:[b-10:-1]}", v[-3:-1])
        self._run_test("{j:[b5:]}"    , v[2:])
        self._run_test("{j:[b50:]}"   , v[50:])
        self._run_test("{j:[b:5]}"    , v[:1])
        self._run_test("{j:[b:50]}"   , v[:50])
        self._run_test("{j:[b:]}"     , v)
        self._run_test("{j:[b::]}"    , v)

    def test_maxlen(self):
        v = self.kwdict["a"]
        self._run_test("{a:L5/foo/}" , "foo")
        self._run_test("{a:L50/foo/}", v)
        self._run_test("{a:L50/foo/>50}", " " * 39 + v)
        self._run_test("{a:L50/foo/>51}", "foo")
        self._run_test("{a:Lab/foo/}", "foo")

    def test_join(self):
        self._run_test("{l:J}"       , "abc")
        self._run_test("{l:J,}"      , "a,b,c")
        self._run_test("{l:J,/}"     , "a,b,c")
        self._run_test("{l:J,/>20}"  , "               a,b,c")
        self._run_test("{l:J - }"    , "a - b - c")
        self._run_test("{l:J - /}"   , "a - b - c")
        self._run_test("{l:J - />20}", "           a - b - c")

        self._run_test("{a:J/}"      , self.kwdict["a"])
        self._run_test("{a:J, /}"    , self.kwdict["a"])

    def test_replace(self):
        self._run_test("{a:Rh/C/}"  , "CElLo wOrLd")
        self._run_test("{a!l:Rh/C/}", "Cello world")
        self._run_test("{a!u:Rh/C/}", "HELLO WORLD")

        self._run_test("{a!l:Rl/_/}", "he__o wor_d")
        self._run_test("{a!l:Rl//}" , "heo word")
        self._run_test("{name:Rame/othing/}", "Nothing")

    def test_datetime(self):
        self._run_test("{ds:D%Y-%m-%dT%H:%M:%S%z}", "2010-01-01 00:00:00")
        self._run_test("{ds:D%Y}", "2010-01-01T01:00:00+0100")
        self._run_test("{l:D%Y}", "None")

    def test_offset(self):
        self._run_test("{dt:O 01:00}", "2010-01-01 01:00:00")
        self._run_test("{dt:O+02:00}", "2010-01-01 02:00:00")
        self._run_test("{dt:O-03:45}", "2009-12-31 20:15:00")

        self._run_test("{dt:O12}", "2010-01-01 12:00:00")
        self._run_test("{dt:O-24}", "2009-12-31 00:00:00")

        self._run_test("{ds:D%Y-%m-%dT%H:%M:%S%z/O1}", "2010-01-01 01:00:00")
        self._run_test("{t!d:O2}", "2010-01-01 02:00:00")

    def test_offset_local(self):
        ts = self.kwdict["dt"].replace(
            tzinfo=datetime.timezone.utc).timestamp()
        offset = time.localtime(ts).tm_gmtoff
        dt = self.kwdict["dt"] + datetime.timedelta(seconds=offset)
        self._run_test("{dt:O}", str(dt))
        self._run_test("{dt:Olocal}", str(dt))

        ts = self.kwdict["dt_dst"].replace(
            tzinfo=datetime.timezone.utc).timestamp()
        offset = time.localtime(ts).tm_gmtoff
        dt = self.kwdict["dt_dst"] + datetime.timedelta(seconds=offset)
        self._run_test("{dt_dst:O}", str(dt))
        self._run_test("{dt_dst:Olocal}", str(dt))

    def test_sort(self):
        self._run_test("{l:S}" , "['a', 'b', 'c']")
        self._run_test("{l:Sa}", "['a', 'b', 'c']")
        self._run_test("{l:Sd}", "['c', 'b', 'a']")
        self._run_test("{l:Sr}", "['c', 'b', 'a']")

        self._run_test(
            "{a:S}", "[' ', 'E', 'L', 'L', 'O', 'd', 'h', 'l', 'o', 'r', 'w']")
        self._run_test(
            "{a:S-asc}",  # starts with 'S', contains 'a'
            "[' ', 'E', 'L', 'L', 'O', 'd', 'h', 'l', 'o', 'r', 'w']")
        self._run_test(
            "{a:Sort-reverse}",  # starts with 'S', contains 'r'
            "['w', 'r', 'o', 'l', 'h', 'd', 'O', 'L', 'L', 'E', ' ']")

    def test_chain_special(self):
        # multiple replacements
        self._run_test("{a:Rh/C/RE/e/RL/l/}", "Cello wOrld")
        self._run_test("{d[b]!s:R1/Q/R2/A/R0/Y/}", "Y")

        # join-and-replace
        self._run_test("{l:J-/Rb/E/}", "a-E-c")

        # join and slice
        self._run_test("{l:J-/[1:-1]}", "-b-")

        # optional-and-maxlen
        self._run_test("{d[a]:?</>/L1/too long/}", "<too long>")
        self._run_test("{d[c]:?</>/L5/too long/}", "")

        # parse and format datetime
        self._run_test("{ds:D%Y-%m-%dT%H:%M:%S%z/%Y%m%d}", "20100101")

        # sort and join
        self._run_test("{a:S/J}", " ELLOdhlorw")

    def test_separator(self):
        orig_separator = formatter._SEPARATOR
        try:
            formatter._SEPARATOR = "|"
            self._run_test("{a:Rh|C|RE|e|RL|l|}", "Cello wOrld")
            self._run_test("{d[b]!s:R1|Q|R2|A|R0|Y|}", "Y")

            formatter._SEPARATOR = "##"
            self._run_test("{l:J-##Rb##E##}", "a-E-c")
            self._run_test("{l:J-##[1:-1]}", "-b-")

            formatter._SEPARATOR = "\0"
            self._run_test("{d[a]:?<\0>\0L1\0too long\0}", "<too long>")
            self._run_test("{d[c]:?<\0>\0L5\0too long\0}", "")

            formatter._SEPARATOR = "?"
            self._run_test("{ds:D%Y-%m-%dT%H:%M:%S%z?%Y%m%d}", "20100101")
        finally:
            formatter._SEPARATOR = orig_separator

    def test_globals_env(self):
        os.environ["FORMATTER_TEST"] = value = self.kwdict["a"]

        self._run_test("{_env[FORMATTER_TEST]}"  , value)
        self._run_test("{_env[FORMATTER_TEST]!l}", value.lower())
        self._run_test("{z|_env[FORMATTER_TEST]}", value)

    def test_globals_now(self):
        fmt = formatter.parse("{_now}")
        out1 = fmt.format_map(self.kwdict)
        self.assertRegex(out1, r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d(\.\d+)?$")

        out = formatter.parse("{_now:%Y%m%d}").format_map(self.kwdict)
        now = datetime.datetime.now()
        self.assertRegex(out, r"^\d{8}$")
        self.assertEqual(out, format(now, "%Y%m%d"))

        out = formatter.parse("{z|_now:%Y}").format_map(self.kwdict)
        self.assertRegex(out, r"^\d{4}$")
        self.assertEqual(out, format(now, "%Y"))

        out2 = fmt.format_map(self.kwdict)
        self.assertRegex(out1, r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d(\.\d+)?$")
        self.assertNotEqual(out1, out2)

    def test_literals(self):
        value = "foo"

        self._run_test("{'foo'}"       , value)
        self._run_test("{'foo'!u}"     , value.upper())
        self._run_test("{'f00':R0/o/}" , value)
        self._run_test("{'foobar'[:3]}", value)
        self._run_test("{z|'foo'}"     , value)
        self._run_test("{z|''|'foo'}"  , value)
        self._run_test("{z|''}"        , "")
        self._run_test("{''|''}"       , "")

        self._run_test("{_lit[foo]}"       , value)
        self._run_test("{_lit[foo]!u}"     , value.upper())
        self._run_test("{_lit[f00]:R0/o/}" , value)
        self._run_test("{_lit[foobar][:3]}", value)
        self._run_test("{z|_lit[foo]}"     , value)

    def test_template(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            path1 = os.path.join(tmpdirname, "tpl1")
            path2 = os.path.join(tmpdirname, "tpl2")

            with open(path1, "w") as fp:
                fp.write("{a}")
            fmt1 = formatter.parse("\fT " + path1)

            with open(path2, "w") as fp:
                fp.write("{a!u:Rh/C/}\nFooBar")
            fmt2 = formatter.parse("\fT " + path2)

        self.assertEqual(fmt1.format_map(self.kwdict), self.kwdict["a"])
        self.assertEqual(fmt2.format_map(self.kwdict), "HELLO WORLD\nFooBar")

        with self.assertRaises(OSError):
            formatter.parse("\fT /")

    def test_expression(self):
        self._run_test("\fE a", self.kwdict["a"])
        self._run_test("\fE name * 2 + ' ' + a", "{}{} {}".format(
            self.kwdict["name"], self.kwdict["name"], self.kwdict["a"]))

    @unittest.skipIf(sys.hexversion < 0x3060000, "no fstring support")
    def test_fstring(self):
        self._run_test("\fF {a}", self.kwdict["a"])
        self._run_test("\fF {name}{name} {a}", "{}{} {}".format(
            self.kwdict["name"], self.kwdict["name"], self.kwdict["a"]))
        self._run_test("\fF foo-'\"{a.upper()}\"'-bar",
                       """foo-'"{}"'-bar""".format(self.kwdict["a"].upper()))

    @unittest.skipIf(sys.hexversion < 0x3060000, "no fstring support")
    def test_template_fstring(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            path1 = os.path.join(tmpdirname, "tpl1")
            path2 = os.path.join(tmpdirname, "tpl2")

            with open(path1, "w") as fp:
                fp.write("{a}")
            fmt1 = formatter.parse("\fTF " + path1)

            with open(path2, "w") as fp:
                fp.write("foo-'\"{a.upper()}\"'-bar")
            fmt2 = formatter.parse("\fTF " + path2)

        self.assertEqual(fmt1.format_map(self.kwdict), self.kwdict["a"])
        self.assertEqual(fmt2.format_map(self.kwdict),
                         """foo-'"{}"'-bar""".format(self.kwdict["a"].upper()))

        with self.assertRaises(OSError):
            formatter.parse("\fTF /")

    def test_module(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            path = os.path.join(tmpdirname, "testmod.py")

            with open(path, "w") as fp:
                fp.write("""
def gentext(kwdict):
    name = kwdict.get("Name") or kwdict.get("name") or "foo"
    return "'{title1}' by {}".format(name, **kwdict)

def lengths(kwdict):
    a = 0
    for k, v in kwdict.items():
        try:
            a += len(v)
        except TypeError:
            pass
    return format(a)

def noarg():
    return ""
""")
            sys.path.insert(0, tmpdirname)
            try:
                fmt1 = formatter.parse("\fM testmod:gentext")
                fmt2 = formatter.parse("\fM testmod:lengths")
                fmt0 = formatter.parse("\fM testmod:noarg")

                with self.assertRaises(AttributeError):
                    formatter.parse("\fM testmod:missing")
                with self.assertRaises(ImportError):
                    formatter.parse("\fM missing:missing")
            finally:
                sys.path.pop(0)

            fmt3 = formatter.parse("\fM " + path + ":gentext")
            fmt4 = formatter.parse("\fM " + path + ":lengths")

        self.assertEqual(fmt1.format_map(self.kwdict), "'Title' by Name")
        self.assertEqual(fmt2.format_map(self.kwdict), "126")

        self.assertEqual(fmt3.format_map(self.kwdict), "'Title' by Name")
        self.assertEqual(fmt4.format_map(self.kwdict), "126")

        with self.assertRaises(TypeError):
            self.assertEqual(fmt0.format_map(self.kwdict), "")

    def _run_test(self, format_string, result, default=None, fmt=format):
        fmt = formatter.parse(format_string, default, fmt)
        output = fmt.format_map(self.kwdict)
        self.assertEqual(output, result, format_string)


if __name__ == "__main__":
    unittest.main()
