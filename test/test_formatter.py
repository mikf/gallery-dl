#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-2025 Mike Fährmann
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
from gallery_dl import formatter, text, dt, util, config  # noqa E402

try:
    import jinja2
except ImportError:
    jinja2 = None


class TestFormatter(unittest.TestCase):

    def tearDown(self):
        config.clear()

    kwdict = {
        "a": "hElLo wOrLd",
        "b": "äöü",
        "j": "げんそうきょう",
        "d": {"a": "foo", "b": 0, "c": None},
        "i": 2,
        "l": ["a", "b", "c"],
        "L": [
            {"name": "John Doe"      , "age": 42, "email": "jd@example.org"},
            {"name": "Jane Smith"    , "age": 24, "email": None},
            {"name": "Max Mustermann", "age": False},
        ],
        "n": None,
        "s": " \n\r\tSPACE    ",
        "S": " \n\r\tS  P         A\tC\nE    ",
        "h": "<p>foo </p> &amp; bar <p> </p>",
        "H": """<p>
  <a href="http://www.example.com">Lorem ipsum dolor sit amet</a>.
  Duis aute irure <a href="http://blog.example.org/lorem?foo=bar">
  http://blog.example.org</a>.
</p>""",
        "u": "&#x27;&lt; / &gt;&#x27;",
        "t": 1262304000,
        "ds": "2010-01-01T01:00:00+01:00",
        "dt": datetime.datetime(2010, 1, 1),
        "dt_dst": datetime.datetime(2010, 6, 1),
        "i_str": "12345",
        "f_str": "12.45",
        "lang": "en",
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
        self._run_test("{S!t}", "S  P         A\tC\nE")
        self._run_test("{a!U}", self.kwdict["a"])
        self._run_test("{u!U}", "'< / >'")
        self._run_test("{a!H}", self.kwdict["a"])
        self._run_test("{h!H}", "foo & bar")
        self._run_test("{u!H}", "'< / >'")
        self._run_test("{n!H}", "")
        self._run_test("{h!R}", [])
        self._run_test("{H!R}", ["http://www.example.com",
                                 "http://blog.example.org/lorem?foo=bar",
                                 "http://blog.example.org"])
        self._run_test("{a!s}", self.kwdict["a"])
        self._run_test("{a!r}", f"'{self.kwdict['a']}'")
        self._run_test("{a!a}", f"'{self.kwdict['a']}'")
        self._run_test("{b!a}", "'\\xe4\\xf6\\xfc'")
        self._run_test("{a!S}", self.kwdict["a"])
        self._run_test("{l!S}", "a, b, c")
        self._run_test("{n!S}", "")
        self._run_test("{t!d}", datetime.datetime(2010, 1, 1))
        self._run_test("{t!d:%Y-%m-%d}", "2010-01-01")
        self._run_test("{t!D}" , datetime.datetime(2010, 1, 1))
        self._run_test("{ds!D}", datetime.datetime(2010, 1, 1))
        self._run_test("{dt!D}", datetime.datetime(2010, 1, 1))
        self._run_test("{t!D:%Y-%m-%d}", "2010-01-01")
        self._run_test("{dt!T}", "1262304000")
        self._run_test("{l!j}", '["a","b","c"]')
        self._run_test("{dt!j}", '"2010-01-01 00:00:00"')
        self._run_test("{a!g}", "hello-world")
        self._run_test("{lang!L}", "English")
        self._run_test("{'fr'!L}", "French")
        self._run_test("{a!L}", None)
        self._run_test("{a!n}", 11)
        self._run_test("{l!n}", 3)
        self._run_test("{d!n}", 3)
        self._run_test("{s!W}", "SPACE")
        self._run_test("{S!W}", "S P A C E")
        self._run_test("{i_str!i}", 12345)
        self._run_test("{i_str!f}", 12345.0)
        self._run_test("{f_str!f}", 12.45)

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
        self._run_test("{missing:?a//}", f"a{default}", default)

    def test_fmt_func(self):
        self._run_test("{t}" , self.kwdict["t"] , None, int)
        self._run_test("{t}" , self.kwdict["t"] , None, util.identity)
        self._run_test("{dt}", self.kwdict["dt"], None, util.identity)
        self._run_test("{ds}", self.kwdict["dt"], None, dt.parse_iso)
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

    def test_indexing_negative(self):
        self._run_test("{l[-1]}" , "c")
        self._run_test("{a[-7]}" , "o")
        self._run_test("{a[-0]}" , "h")  # same as a[0]

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

    def test_specifier_maxlen(self):
        v = self.kwdict["a"]
        self._run_test("{a:L5/foo/}" , "foo")
        self._run_test("{a:L50/foo/}", v)
        self._run_test("{a:L50/foo/>50}", " " * 39 + v)
        self._run_test("{a:L50/foo/>51}", "foo")
        self._run_test("{a:Lab/foo/}", "foo")

    def test_specifier_maxlen_bytes(self):
        v = self.kwdict["a"]
        self._run_test("{a:Lb5/foo/}" , "foo")
        self._run_test("{a:Lb50/foo/}", v)
        self._run_test("{a:Lb50/foo/>50}", " " * 39 + v)
        self._run_test("{a:Lb50/foo/>51}", "foo")
        self._run_test("{a:Lbab/foo/}", "foo")

        v = self.kwdict["j"]
        self._run_test("{j:Lb5/foo/}" , "foo")
        self._run_test("{j:Lb50/foo/}", v)
        self._run_test("{j:Lbab/foo/}", "foo")

    def test_specifier_join(self):
        self._run_test("{l:J}"       , "abc")
        self._run_test("{l:J,}"      , "a,b,c")
        self._run_test("{l:J,/}"     , "a,b,c")
        self._run_test("{l:J,/>20}"  , "               a,b,c")
        self._run_test("{l:J - }"    , "a - b - c")
        self._run_test("{l:J - /}"   , "a - b - c")
        self._run_test("{l:J - />20}", "           a - b - c")

        self._run_test("{a:J/}"      , self.kwdict["a"])
        self._run_test("{a:J, /}"    , self.kwdict["a"])

    def test_specifier_replace(self):
        self._run_test("{a:Rh/C/}"  , "CElLo wOrLd")
        self._run_test("{a!l:Rh/C/}", "Cello world")
        self._run_test("{a!u:Rh/C/}", "HELLO WORLD")

        self._run_test("{a!l:Rl/_/}", "he__o wor_d")
        self._run_test("{a!l:Rl//}" , "heo word")
        self._run_test("{name:Rame/othing/}", "Nothing")

    def test_specifier_datetime(self):
        self._run_test("{ds:D%Y-%m-%dT%H:%M:%S%z}", "2010-01-01 00:00:00")
        self._run_test("{ds:D%Y}", "[Invalid DateTime]")
        self._run_test("{l2:D%Y}", "[Invalid DateTime]")

    def test_specifier_offset(self):
        self._run_test("{dt:O 01:00}", "2010-01-01 01:00:00")
        self._run_test("{dt:O+02:00}", "2010-01-01 02:00:00")
        self._run_test("{dt:O-03:45}", "2009-12-31 20:15:00")

        self._run_test("{dt:O12}", "2010-01-01 12:00:00")
        self._run_test("{dt:O-24}", "2009-12-31 00:00:00")

        self._run_test("{ds:D%Y-%m-%dT%H:%M:%S%z/O1}", "2010-01-01 01:00:00")
        self._run_test("{t!d:O2}", "2010-01-01 02:00:00")

    def test_specifier_offset_local(self):
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

    def test_specifier_sort(self):
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

    def test_specifier_arithmetic(self):
        self._run_test("{i:A+1}", "3")
        self._run_test("{i:A-1}", "1")
        self._run_test("{i:A*3}", "6")

    def test_specifier_conversions(self):
        self._run_test("{a:Cl}"   , "hello world")
        self._run_test("{h:CHC}"  , "Foo & Bar")
        self._run_test("{l:CSulc}", "A, b, c")

    def test_specifier_limit(self):
        self._run_test("{a:X20/ */}", "hElLo wOrLd")
        self._run_test("{a:X10/ */}", "hElLo wO *")

        with self.assertRaises(ValueError):
            self._run_test("{a:Xfoo/ */}", "hello wo *")

    def test_specifier_limit_bytes(self):
        self._run_test("{a:Xb20/ */}", "hElLo wOrLd")
        self._run_test("{a:Xb10/ */}", "hElLo wO *")

        self._run_test("{j:Xb50/〜/}", "げんそうきょう")
        self._run_test("{j:Xb20/〜/}", "げんそうき〜")
        self._run_test("{j:Xb20/ */}", "げんそうきょ *")

        with self.assertRaises(ValueError):
            self._run_test("{a:Xbfoo/ */}", "hello wo *")

    def test_specifier_map(self):
        self._run_test("{L:Mname/}" ,
                       "['John Doe', 'Jane Smith', 'Max Mustermann']")
        self._run_test("{L:Mage/}"  ,
                       "[42, 24, False]")

        self._run_test("{a:Mname}", self.kwdict["a"])
        self._run_test("{n:Mname}", "None")
        self._run_test("{title4:Mname}", "0")

        with self.assertRaises(ValueError):
            self._run_test("{t:Mname", "")

    def test_specifier_identity(self):
        self._run_test("{a:I}", self.kwdict["a"])
        self._run_test("{i:I}", self.kwdict["i"])
        self._run_test("{dt:I}", self.kwdict["dt"])

        self._run_test("{t!D:I}", self.kwdict["dt"])
        self._run_test("{t!D:I/O+01:30}", self.kwdict["dt"])
        self._run_test("{i:A+1/I}", self.kwdict["i"]+1)

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

        # map and join
        self._run_test("{L:Mname/J-}", "John Doe-Jane Smith-Max Mustermann")

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

    def test_globals_nul(self):
        value = "None"

        self._run_test("{_nul}"         , value)
        self._run_test("{_nul[key]}"    , value)
        self._run_test("{z|_nul}"       , value)
        self._run_test("{z|_nul:%Y%m%s}", value)

    def test_literals(self):
        value = "foo"

        self._run_test("{'foo'}"      , value)
        self._run_test("{'foo'!u}"    , value.upper())
        self._run_test("{'f00':R0/o/}", value)

        self._run_test("{z|'foo'}"      , value)
        self._run_test("{z|''|'foo'}"   , value)
        self._run_test("{z|'foo'!u}"    , value.upper())
        self._run_test("{z|'f00':R0/o/}", value)

        self._run_test("{_lit[foo]}"       , value)
        self._run_test("{_lit[foo]!u}"     , value.upper())
        self._run_test("{_lit[f00]:R0/o/}" , value)
        self._run_test("{_lit[foobar][:3]}", value)
        self._run_test("{z|_lit[foo]}"     , value)

        # empty (#4492)
        self._run_test("{z|''}" , "")
        self._run_test("{''|''}", "")

        # special characters (dots, brackets, singlee quotes) (#5539)
        self._run_test("{'f.o.o'}"    , "f.o.o")
        self._run_test("{_lit[f.o.o]}", "f.o.o")
        self._run_test("{_lit[f'o'o]}", "f'o'o")
        self._run_test("{'f.[].[]'}"  , "f.[].[]")
        self._run_test("{z|'f.[].[]'}", "f.[].[]")

    def test_template(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            path1 = os.path.join(tmpdirname, "tpl1")
            path2 = os.path.join(tmpdirname, "tpl2")

            with open(path1, "w") as fp:
                fp.write("{a}")
            fmt1 = formatter.parse(f"\fT {path1}")

            with open(path2, "w") as fp:
                fp.write("{a!u:Rh/C/}\nFooBar")
            fmt2 = formatter.parse(f"\fT {path2}")

        self.assertEqual(fmt1.format_map(self.kwdict), self.kwdict["a"])
        self.assertEqual(fmt2.format_map(self.kwdict), "HELLO WORLD\nFooBar")

        with self.assertRaises(OSError):
            formatter.parse("\fT /")

    def test_expression(self):
        self._run_test("\fE a", self.kwdict["a"])
        self._run_test(
            "\fE name * 2 + ' ' + a",
            f"{self.kwdict['name']}{self.kwdict['name']} {self.kwdict['a']}")

    def test_fstring(self):
        self._run_test("\fF {a}", self.kwdict["a"])
        self._run_test(
            "\fF {name}{name} {a}",
            f"{self.kwdict['name']}{self.kwdict['name']} {self.kwdict['a']}")
        self._run_test(
            "\fF foo-'\"{a.upper()}\"'-bar",
            f"""foo-'"{self.kwdict['a'].upper()}"'-bar""")

    def test_template_fstring(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            path1 = os.path.join(tmpdirname, "tpl1")
            path2 = os.path.join(tmpdirname, "tpl2")

            with open(path1, "w") as fp:
                fp.write("{a}")
            fmt1 = formatter.parse(f"\fTF {path1}")

            with open(path2, "w") as fp:
                fp.write("foo-'\"{a.upper()}\"'-bar")
            fmt2 = formatter.parse(f"\fTF {path2}")

        self.assertEqual(fmt1.format_map(self.kwdict), self.kwdict["a"])
        self.assertEqual(fmt2.format_map(self.kwdict),
                         f"""foo-'"{self.kwdict['a'].upper()}"'-bar""")

        with self.assertRaises(OSError):
            formatter.parse("\fTF /")

    @unittest.skipIf(jinja2 is None, "no jinja2")
    def test_jinja(self):
        formatter.JinjaFormatter.env = None

        self._run_test("\fJ {{a}}", self.kwdict["a"])
        self._run_test(
            "\fJ {{name}}{{name}} {{a}}",
            f"{self.kwdict['name']}{self.kwdict['name']} {self.kwdict['a']}")
        self._run_test(
            "\fJ foo-'\"{{a | upper}}\"'-bar",
            f"""foo-'"{self.kwdict['a'].upper()}"'-bar""")

    @unittest.skipIf(jinja2 is None, "no jinja2")
    def test_template_jinja(self):
        formatter.JinjaFormatter.env = None

        with tempfile.TemporaryDirectory() as tmpdirname:
            path1 = os.path.join(tmpdirname, "tpl1")
            path2 = os.path.join(tmpdirname, "tpl2")

            with open(path1, "w") as fp:
                fp.write("{{a}}")
            fmt1 = formatter.parse(f"\fTJ {path1}")

            with open(path2, "w") as fp:
                fp.write("foo-'\"{{a | upper}}\"'-bar")
            fmt2 = formatter.parse(f"\fTJ {path2}")

        self.assertEqual(fmt1.format_map(self.kwdict), self.kwdict["a"])
        self.assertEqual(fmt2.format_map(self.kwdict),
                         f"""foo-'"{self.kwdict['a'].upper()}"'-bar""")

        with self.assertRaises(OSError):
            formatter.parse("\fTJ /")

    @unittest.skipIf(jinja2 is None, "no jinja2")
    def test_template_jinja_opts(self):
        formatter.JinjaFormatter.env = None

        with tempfile.TemporaryDirectory() as tmpdirname:
            path_filters = os.path.join(tmpdirname, "jinja_filters.py")
            path_template = os.path.join(tmpdirname, "jinja_template.txt")

            config.set((), "jinja", {
                "environment": {
                    "variable_start_string": "(((",
                    "variable_end_string"  : ")))",
                    "keep_trailing_newline": True,
                },
                "filters": path_filters,
            })

            with open(path_filters, "w") as fp:
                fp.write(r"""
import re

def datetime_format(value, format="%H:%M %d-%m-%y"):
    return value.strftime(format)

def sanitize(value):
    return re.sub(r"\s+", " ", value.strip())

__filters__ = {
    "dt_fmt": datetime_format,
    "sanitize_whitespace": sanitize,
}
""")

            with open(path_template, "w") as fp:
                fp.write("""\
Present Day  is ((( dt | dt_fmt("%B %d, %Y") )))
Present Time is ((( dt | dt_fmt("%H:%M:%S") )))

Hello ((( s | sanitize_whitespace ))).
I hope there is enough "(((S|sanitize_whitespace)))" for you.
""")
            fmt = formatter.parse(f"\fTJ {path_template}")

        self.assertEqual(fmt.format_map(self.kwdict), """\
Present Day  is January 01, 2010
Present Time is 00:00:00

Hello SPACE.
I hope there is enough "S P A C E" for you.
""")

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
        if k == k.lower():
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

            fmt3 = formatter.parse(f"\fM {path}:gentext")
            fmt4 = formatter.parse(f"\fM {path}:lengths")

        self.assertEqual(fmt1.format_map(self.kwdict), "'Title' by Name")
        self.assertEqual(fmt2.format_map(self.kwdict), "139")

        self.assertEqual(fmt3.format_map(self.kwdict), "'Title' by Name")
        self.assertEqual(fmt4.format_map(self.kwdict), "139")

        with self.assertRaises(TypeError):
            self.assertEqual(fmt0.format_map(self.kwdict), "")

    def _run_test(self, format_string, result, default=None, fmt=format):
        fmt = formatter.parse(format_string, default, fmt)
        output = fmt.format_map(self.kwdict)
        self.assertEqual(output, result, format_string)


if __name__ == "__main__":
    unittest.main()
