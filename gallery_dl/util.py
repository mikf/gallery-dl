# -*- coding: utf-8 -*-

# Copyright 2017-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Utility functions and classes"""

import re
import os
import sys
import json
import time
import random
import getpass
import hashlib
import binascii
import datetime
import functools
import itertools
import subprocess
import collections
import urllib.parse
from http.cookiejar import Cookie
from email.utils import mktime_tz, parsedate_tz
from . import text, version, exception


def bencode(num, alphabet="0123456789"):
    """Encode an integer into a base-N encoded string"""
    data = ""
    base = len(alphabet)
    while num:
        num, remainder = divmod(num, base)
        data = alphabet[remainder] + data
    return data


def bdecode(data, alphabet="0123456789"):
    """Decode a base-N encoded string ( N = len(alphabet) )"""
    num = 0
    base = len(alphabet)
    for c in data:
        num *= base
        num += alphabet.index(c)
    return num


def decrypt_xor(encrypted, key, base64=True, fromhex=False):
    if base64:
        encrypted = binascii.a2b_base64(encrypted)
    if fromhex:
        encrypted = bytes.fromhex(encrypted.decode())

    div = len(key)
    return bytes([
        encrypted[i] ^ key[i % div]
        for i in range(len(encrypted))
    ]).decode()


def advance(iterable, num):
    """"Advance 'iterable' by 'num' steps"""
    iterator = iter(iterable)
    next(itertools.islice(iterator, num, num), None)
    return iterator


def repeat(times):
    """Return an iterator that returns None"""
    if times < 0:
        return itertools.repeat(None)
    return itertools.repeat(None, times)


def unique(iterable):
    """Yield unique elements from 'iterable' while preserving order"""
    seen = set()
    add = seen.add
    for element in iterable:
        if element not in seen:
            add(element)
            yield element


def unique_sequence(iterable):
    """Yield sequentially unique elements from 'iterable'"""
    last = None
    for element in iterable:
        if element != last:
            last = element
            yield element


def contains(values, elements, separator=" "):
    """Returns True if at least one of 'elements' is contained in 'values'"""
    if isinstance(values, str) and (separator or separator is None):
        values = values.split(separator)

    if not isinstance(elements, (tuple, list)):
        return elements in values

    for e in elements:
        if e in values:
            return True
    return False


def raises(cls):
    """Returns a function that raises 'cls' as exception"""
    def wrap(*args):
        raise cls(*args)
    return wrap


def identity(x, _=None):
    """Returns its argument"""
    return x


def true(_, __=None):
    """Always returns True"""
    return True


def false(_, __=None):
    """Always returns False"""
    return False


def noop():
    """Does nothing"""


def md5(s):
    """Generate MD5 hexdigest of 's'"""
    if not s:
        s = b""
    elif isinstance(s, str):
        s = s.encode()
    return hashlib.md5(s).hexdigest()


def sha1(s):
    """Generate SHA1 hexdigest of 's'"""
    if not s:
        s = b""
    elif isinstance(s, str):
        s = s.encode()
    return hashlib.sha1(s).hexdigest()


def generate_token(size=16):
    """Generate a random token with hexadecimal digits"""
    data = random.getrandbits(size * 8).to_bytes(size, "big")
    return binascii.hexlify(data).decode()


def format_value(value, suffixes="kMGTPEZY"):
    value = format(value)
    value_len = len(value)
    index = value_len - 4
    if index >= 0:
        offset = (value_len - 1) % 3 + 1
        return (value[:offset] + "." + value[offset:offset+2] +
                suffixes[index // 3])
    return value


def combine_dict(a, b):
    """Recursively combine the contents of 'b' into 'a'"""
    for key, value in b.items():
        if key in a and isinstance(value, dict) and isinstance(a[key], dict):
            combine_dict(a[key], value)
        else:
            a[key] = value
    return a


def transform_dict(a, func):
    """Recursively apply 'func' to all values in 'a'"""
    for key, value in a.items():
        if isinstance(value, dict):
            transform_dict(value, func)
        else:
            a[key] = func(value)


def filter_dict(a):
    """Return a copy of 'a' without "private" entries"""
    return {k: v for k, v in a.items() if k[0] != "_"}


def delete_items(obj, keys):
    """Remove all 'keys' from 'obj'"""
    for key in keys:
        if key in obj:
            del obj[key]


def enumerate_reversed(iterable, start=0, length=None):
    """Enumerate 'iterable' and return its elements in reverse order"""
    if length is None:
        length = len(iterable)

    try:
        iterable = zip(range(start-1+length, start-1, -1), reversed(iterable))
    except TypeError:
        iterable = list(zip(range(start, start+length), iterable))
        iterable.reverse()

    return iterable


def number_to_string(value, numbers=(int, float)):
    """Convert numbers (int, float) to string; Return everything else as is."""
    return str(value) if value.__class__ in numbers else value


def to_string(value):
    """str() with "better" defaults"""
    if not value:
        return ""
    if value.__class__ is list:
        try:
            return ", ".join(value)
        except Exception:
            return ", ".join(map(str, value))
    return str(value)


def datetime_to_timestamp(dt):
    """Convert naive UTC datetime to Unix timestamp"""
    return (dt - EPOCH) / SECOND


def datetime_to_timestamp_string(dt):
    """Convert naive UTC datetime to Unix timestamp string"""
    try:
        return str((dt - EPOCH) // SECOND)
    except Exception:
        return ""


if sys.hexversion < 0x30c0000:
    # Python <= 3.11
    datetime_utcfromtimestamp = datetime.datetime.utcfromtimestamp
    datetime_utcnow = datetime.datetime.utcnow
    datetime_from_timestamp = datetime_utcfromtimestamp
else:
    # Python >= 3.12
    def datetime_from_timestamp(ts=None):
        """Convert Unix timestamp to naive UTC datetime"""
        Y, m, d, H, M, S, _, _, _ = time.gmtime(ts)
        return datetime.datetime(Y, m, d, H, M, S)

    datetime_utcfromtimestamp = datetime_from_timestamp
    datetime_utcnow = datetime_from_timestamp


def json_default(obj):
    if isinstance(obj, CustomNone):
        return None
    return str(obj)


json_loads = json._default_decoder.decode
json_dumps = json.JSONEncoder(
    check_circular=False,
    separators=(",", ":"),
    default=json_default,
).encode


def dump_json(obj, fp=sys.stdout, ensure_ascii=True, indent=4):
    """Serialize 'obj' as JSON and write it to 'fp'"""
    json.dump(
        obj, fp,
        ensure_ascii=ensure_ascii,
        indent=indent,
        default=json_default,
        sort_keys=True,
    )
    fp.write("\n")


def dump_response(response, fp, headers=False, content=True, hide_auth=True):
    """Write the contents of 'response' into a file-like object"""

    if headers:
        request = response.request
        req_headers = request.headers.copy()
        res_headers = response.headers.copy()
        outfmt = """\
{request.method} {request.url}
Status: {response.status_code} {response.reason}

Request Headers
---------------
{request_headers}
"""
        if request.body:
            outfmt += """
Request Body
------------
{request.body}
"""
        outfmt += """
Response Headers
----------------
{response_headers}
"""
        if hide_auth:
            authorization = req_headers.get("Authorization")
            if authorization:
                atype, sep, _ = str(authorization).partition(" ")
                req_headers["Authorization"] = atype + " ***" if sep else "***"

            cookie = req_headers.get("Cookie")
            if cookie:
                req_headers["Cookie"] = ";".join(
                    c.partition("=")[0] + "=***"
                    for c in cookie.split(";")
                )

            set_cookie = res_headers.get("Set-Cookie")
            if set_cookie:
                res_headers["Set-Cookie"] = re.sub(
                    r"(^|, )([^ =]+)=[^,;]*", r"\1\2=***", set_cookie,
                )

        fmt_nv = "{}: {}".format

        fp.write(outfmt.format(
            request=request,
            response=response,
            request_headers="\n".join(
                fmt_nv(name, value)
                for name, value in req_headers.items()
            ),
            response_headers="\n".join(
                fmt_nv(name, value)
                for name, value in res_headers.items()
            ),
        ).encode())

    if content:
        if headers:
            fp.write(b"\nContent\n-------\n")
        fp.write(response.content)


def extract_headers(response):
    headers = response.headers
    data = dict(headers)

    hcd = headers.get("content-disposition")
    if hcd:
        name = text.extr(hcd, 'filename="', '"')
        if name:
            text.nameext_from_url(name, data)

    hlm = headers.get("last-modified")
    if hlm:
        data["date"] = datetime.datetime(*parsedate_tz(hlm)[:6])

    return data


def detect_challenge(response):
    server = response.headers.get("server")
    if not server:
        return

    elif server.startswith("cloudflare"):
        if response.status_code not in (403, 503):
            return

        mitigated = response.headers.get("cf-mitigated")
        if mitigated and mitigated.lower() == "challenge":
            return "Cloudflare challenge"

        content = response.content
        if b"_cf_chl_opt" in content or b"jschl-answer" in content:
            return "Cloudflare challenge"
        elif b'name="captcha-bypass"' in content:
            return "Cloudflare CAPTCHA"

    elif server.startswith("ddos-guard"):
        if response.status_code == 403 and \
                b"/ddos-guard/js-challenge/" in response.content:
            return "DDoS-Guard challenge"


@functools.lru_cache(maxsize=None)
def git_head():
    try:
        out, err = Popen(
            ("git", "rev-parse", "--short", "HEAD"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.path.dirname(os.path.abspath(__file__)),
        ).communicate()
        if out and not err:
            return out.decode().rstrip()
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def expand_path(path):
    """Expand environment variables and tildes (~)"""
    if not path:
        return path
    if not isinstance(path, str):
        path = os.path.join(*path)
    return os.path.expandvars(os.path.expanduser(path))


def remove_file(path):
    try:
        os.unlink(path)
    except OSError:
        pass


def remove_directory(path):
    try:
        os.rmdir(path)
    except OSError:
        pass


def set_mtime(path, mtime):
    try:
        if isinstance(mtime, str):
            mtime = mktime_tz(parsedate_tz(mtime))
        os.utime(path, (time.time(), mtime))
    except Exception:
        pass


def cookiestxt_load(fp):
    """Parse a Netscape cookies.txt file and add return its Cookies"""
    cookies = []

    for line in fp:

        line = line.lstrip(" ")
        # strip '#HttpOnly_'
        if line.startswith("#HttpOnly_"):
            line = line[10:]
        # ignore empty lines and comments
        if not line or line[0] in ("#", "$", "\n"):
            continue
        # strip trailing '\n'
        if line[-1] == "\n":
            line = line[:-1]

        domain, domain_specified, path, secure, expires, name, value = \
            line.split("\t")

        if not name:
            name = value
            value = None

        cookies.append(Cookie(
            0, name, value,
            None, False,
            domain,
            domain_specified == "TRUE",
            domain[0] == "." if domain else False,
            path, False,
            secure == "TRUE",
            None if expires == "0" or not expires else expires,
            False, None, None, {},
        ))

    return cookies


def cookiestxt_store(fp, cookies):
    """Write 'cookies' in Netscape cookies.txt format to 'fp'"""
    write = fp.write
    write("# Netscape HTTP Cookie File\n\n")

    for cookie in cookies:
        if not cookie.domain:
            continue

        if cookie.value is None:
            name = ""
            value = cookie.name
        else:
            name = cookie.name
            value = cookie.value

        domain = cookie.domain
        write("\t".join((
            domain,
            "TRUE" if domain and domain[0] == "." else "FALSE",
            cookie.path,
            "TRUE" if cookie.secure else "FALSE",
            "0" if cookie.expires is None else str(cookie.expires),
            name,
            value + "\n",
        )))


def code_to_language(code, default=None):
    """Map an ISO 639-1 language code to its actual name"""
    return CODES.get((code or "").lower(), default)


def language_to_code(lang, default=None):
    """Map a language name to its ISO 639-1 code"""
    if lang is None:
        return default
    lang = lang.capitalize()
    for code, language in CODES.items():
        if language == lang:
            return code
    return default


CODES = {
    "ar": "Arabic",
    "bg": "Bulgarian",
    "ca": "Catalan",
    "cs": "Czech",
    "da": "Danish",
    "de": "German",
    "el": "Greek",
    "en": "English",
    "es": "Spanish",
    "fi": "Finnish",
    "fr": "French",
    "he": "Hebrew",
    "hu": "Hungarian",
    "id": "Indonesian",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "ms": "Malay",
    "nl": "Dutch",
    "no": "Norwegian",
    "pl": "Polish",
    "pt": "Portuguese",
    "ro": "Romanian",
    "ru": "Russian",
    "sv": "Swedish",
    "th": "Thai",
    "tr": "Turkish",
    "vi": "Vietnamese",
    "zh": "Chinese",
}


class HTTPBasicAuth():
    __slots__ = ("authorization",)

    def __init__(self, username, password):
        self.authorization = b"Basic " + binascii.b2a_base64(
            username.encode("latin1") + b":" + str(password).encode("latin1")
        )[:-1]

    def __call__(self, request):
        request.headers["Authorization"] = self.authorization
        return request


class ModuleProxy():
    __slots__ = ()

    def __getitem__(self, key, modules=sys.modules):
        try:
            return modules[key]
        except KeyError:
            pass
        try:
            __import__(key)
        except ImportError:
            modules[key] = NONE
            return NONE
        return modules[key]

    __getattr__ = __getitem__


class LazyPrompt():
    __slots__ = ()

    def __str__(self):
        return getpass.getpass()


class NullContext():
    __slots__ = ()

    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class CustomNone():
    """None-style type that supports more operations than regular None"""
    __slots__ = ()

    __getattribute__ = identity
    __getitem__ = identity
    __iter__ = identity

    def __call__(self, *args, **kwargs):
        return self

    @staticmethod
    def __next__():
        raise StopIteration

    def __eq__(self, other):
        return self is other

    def __ne__(self, other):
        return self is not other

    __lt__ = true
    __le__ = true
    __gt__ = false
    __ge__ = false
    __bool__ = false

    __add__ = identity
    __sub__ = identity
    __mul__ = identity
    __matmul__ = identity
    __truediv__ = identity
    __floordiv__ = identity
    __mod__ = identity

    __radd__ = identity
    __rsub__ = identity
    __rmul__ = identity
    __rmatmul__ = identity
    __rtruediv__ = identity
    __rfloordiv__ = identity
    __rmod__ = identity

    __lshift__ = identity
    __rshift__ = identity
    __and__ = identity
    __xor__ = identity
    __or__ = identity

    __rlshift__ = identity
    __rrshift__ = identity
    __rand__ = identity
    __rxor__ = identity
    __ror__ = identity

    __neg__ = identity
    __pos__ = identity
    __abs__ = identity
    __invert__ = identity

    @staticmethod
    def __len__():
        return 0

    __int__ = __len__
    __hash__ = __len__
    __index__ = __len__

    @staticmethod
    def __format__(_):
        return "None"

    @staticmethod
    def __str__():
        return "None"

    __repr__ = __str__


# v128.0 release on 2024-07-09 has ordinal 739076
# v137.0 release on 2025-04-01 has ordinal 739342
# 735492 == 739076 - 128 * 28
# 735506 == 739342 - 137 * 28
_ff_ver = (datetime.date.today().toordinal() - 735506) // 28

NONE = CustomNone()
EPOCH = datetime.datetime(1970, 1, 1)
SECOND = datetime.timedelta(0, 1)
WINDOWS = (os.name == "nt")
SENTINEL = object()
EXECUTABLE = getattr(sys, "frozen", False)
USERAGENT = "gallery-dl/" + version.__version__
USERAGENT_FIREFOX = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{}.0) "
                     "Gecko/20100101 Firefox/{}.0").format(_ff_ver, _ff_ver)
USERAGENT_CHROME = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 "
                    "Safari/537.36")
SPECIAL_EXTRACTORS = {"oauth", "recursive", "generic"}
GLOBALS = {
    "contains" : contains,
    "parse_int": text.parse_int,
    "urlsplit" : urllib.parse.urlsplit,
    "datetime" : datetime.datetime,
    "timedelta": datetime.timedelta,
    "abort"    : raises(exception.StopExtraction),
    "terminate": raises(exception.TerminateExtraction),
    "restart"  : raises(exception.RestartExtraction),
    "hash_sha1": sha1,
    "hash_md5" : md5,
    "std"      : ModuleProxy(),
    "re"       : re,
}


if EXECUTABLE and hasattr(sys, "_MEIPASS"):
    # https://github.com/pyinstaller/pyinstaller/blob/develop/doc
    # /runtime-information.rst#ld_library_path--libpath-considerations
    _popen_env = os.environ.copy()

    orig = _popen_env.get("LD_LIBRARY_PATH_ORIG")
    if orig is None:
        _popen_env.pop("LD_LIBRARY_PATH", None)
    else:
        _popen_env["LD_LIBRARY_PATH"] = orig

    orig = _popen_env.get("DYLD_LIBRARY_PATH_ORIG")
    if orig is None:
        _popen_env.pop("DYLD_LIBRARY_PATH", None)
    else:
        _popen_env["DYLD_LIBRARY_PATH"] = orig

    del orig

    class Popen(subprocess.Popen):
        def __init__(self, args, **kwargs):
            kwargs["env"] = _popen_env
            subprocess.Popen.__init__(self, args, **kwargs)
else:
    Popen = subprocess.Popen


def compile_expression_raw(expr, name="<expr>", globals=None):
    code_object = compile(expr, name, "eval")
    return functools.partial(eval, code_object, globals or GLOBALS)


def compile_expression_defaultdict(expr, name="<expr>", globals=None):
    global GLOBALS_DEFAULT

    if isinstance(__builtins__, dict):
        # cpython
        GLOBALS_DEFAULT = collections.defaultdict(lambda n=NONE: n, GLOBALS)
    else:
        # pypy3 - insert __builtins__ symbols into globals dict
        GLOBALS_DEFAULT = collections.defaultdict(
            lambda n=NONE: n, __builtins__.__dict__)
        GLOBALS_DEFAULT.update(GLOBALS)

    global compile_expression_defaultdict
    compile_expression_defaultdict = compile_expression_defaultdict_impl
    return compile_expression_defaultdict_impl(expr, name, globals)


def compile_expression_defaultdict_impl(expr, name="<expr>", globals=None):
    code_object = compile(expr, name, "eval")
    return functools.partial(eval, code_object, globals or GLOBALS_DEFAULT)


def compile_expression_tryexcept(expr, name="<expr>", globals=None):
    code_object = compile(expr, name, "eval")

    def _eval(locals=None, globals=(globals or GLOBALS), co=code_object):
        try:
            return eval(co, globals, locals)
        except exception.GalleryDLException:
            raise
        except Exception:
            return NONE

    return _eval


compile_expression = compile_expression_tryexcept


def compile_filter(expr, name="<filter>", globals=None):
    if not isinstance(expr, str):
        expr = "(" + ") and (".join(expr) + ")"
    return compile_expression(expr, name, globals)


def import_file(path):
    """Import a Python module from a filesystem path"""
    path, name = os.path.split(path)

    name, sep, ext = name.rpartition(".")
    if not sep:
        name = ext

    if path:
        path = expand_path(path)
        sys.path.insert(0, path)
        try:
            return __import__(name)
        finally:
            del sys.path[0]
    else:
        return __import__(name.replace("-", "_"))


def build_duration_func(duration, min=0.0):
    if not duration:
        if min:
            return lambda: min
        return None

    if isinstance(duration, str):
        lower, _, upper = duration.partition("-")
        lower = float(lower)
    else:
        try:
            lower, upper = duration
        except TypeError:
            lower, upper = duration, None

    if upper:
        upper = float(upper)
        return functools.partial(
            random.uniform,
            lower if lower > min else min,
            upper if upper > min else min,
        )
    else:
        if lower < min:
            lower = min
        return lambda: lower


def build_extractor_filter(categories, negate=True, special=None):
    """Build a function that takes an Extractor class as argument
    and returns True if that class is allowed by 'categories'
    """
    if isinstance(categories, str):
        categories = categories.split(",")

    catset = set()  # set of categories / basecategories
    subset = set()  # set of subcategories
    catsub = []     # list of category-subcategory pairs

    for item in categories:
        category, _, subcategory = item.partition(":")
        if category and category != "*":
            if subcategory and subcategory != "*":
                catsub.append((category, subcategory))
            else:
                catset.add(category)
        elif subcategory and subcategory != "*":
            subset.add(subcategory)

    if special:
        catset |= special
    elif not catset and not subset and not catsub:
        return true if negate else false

    tests = []

    if negate:
        if catset:
            tests.append(lambda extr:
                         extr.category not in catset and
                         extr.basecategory not in catset)
        if subset:
            tests.append(lambda extr: extr.subcategory not in subset)
    else:
        if catset:
            tests.append(lambda extr:
                         extr.category in catset or
                         extr.basecategory in catset)
        if subset:
            tests.append(lambda extr: extr.subcategory in subset)

    if catsub:
        def test(extr):
            for category, subcategory in catsub:
                if subcategory == extr.subcategory and (
                        category == extr.category or
                        category == extr.basecategory):
                    return not negate
            return negate
        tests.append(test)

    if len(tests) == 1:
        return tests[0]
    if negate:
        return lambda extr: all(t(extr) for t in tests)
    else:
        return lambda extr: any(t(extr) for t in tests)


def build_proxy_map(proxies, log=None):
    """Generate a proxy map"""
    if not proxies:
        return None

    if isinstance(proxies, str):
        if "://" not in proxies:
            proxies = "http://" + proxies.lstrip("/")
        return {"http": proxies, "https": proxies}

    if isinstance(proxies, dict):
        for scheme, proxy in proxies.items():
            if "://" not in proxy:
                proxies[scheme] = "http://" + proxy.lstrip("/")
        return proxies

    if log:
        log.warning("invalid proxy specifier: %s", proxies)


def build_predicate(predicates):
    if not predicates:
        return lambda url, kwdict: True
    elif len(predicates) == 1:
        return predicates[0]
    return functools.partial(chain_predicates, predicates)


def chain_predicates(predicates, url, kwdict):
    for pred in predicates:
        if not pred(url, kwdict):
            return False
    return True


class RangePredicate():
    """Predicate; True if the current index is in the given range(s)"""

    def __init__(self, rangespec):
        self.ranges = ranges = self._parse(rangespec)
        self.index = 0

        if ranges:
            # technically wrong, but good enough for now
            # and evaluating min/max for a large range is slow
            self.lower = min(r.start for r in ranges)
            self.upper = max(r.stop for r in ranges) - 1
        else:
            self.lower = 0
            self.upper = 0

    def __call__(self, _url, _kwdict):
        self.index = index = self.index + 1

        if index > self.upper:
            raise exception.StopExtraction()

        for range in self.ranges:
            if index in range:
                return True
        return False

    @staticmethod
    def _parse(rangespec):
        """Parse an integer range string and return the resulting ranges

        Examples:
            _parse("-2,4,6-8,10-")      -> [(1,3), (4,5), (6,9), (10,INTMAX)]
            _parse(" - 3 , 4-  4, 2-6") -> [(1,4), (4,5), (2,7)]
            _parse("1:2,4:8:2")         -> [(1,1), (4,7,2)]
        """
        ranges = []
        append = ranges.append

        if isinstance(rangespec, str):
            rangespec = rangespec.split(",")

        for group in rangespec:
            if not group:
                continue

            elif ":" in group:
                start, _, stop = group.partition(":")
                stop, _, step = stop.partition(":")
                append(range(
                    int(start) if start.strip() else 1,
                    int(stop) if stop.strip() else sys.maxsize,
                    int(step) if step.strip() else 1,
                ))

            elif "-" in group:
                start, _, stop = group.partition("-")
                append(range(
                    int(start) if start.strip() else 1,
                    int(stop) + 1 if stop.strip() else sys.maxsize,
                ))

            else:
                start = int(group)
                append(range(start, start+1))

        return ranges


class UniquePredicate():
    """Predicate; True if given URL has not been encountered before"""
    def __init__(self):
        self.urls = set()

    def __call__(self, url, _):
        if url.startswith("text:"):
            return True
        if url not in self.urls:
            self.urls.add(url)
            return True
        return False


class FilterPredicate():
    """Predicate; True if evaluating the given expression returns True"""

    def __init__(self, expr, target="image"):
        name = "<{} filter>".format(target)
        self.expr = compile_filter(expr, name)

    def __call__(self, _, kwdict):
        try:
            return self.expr(kwdict)
        except exception.GalleryDLException:
            raise
        except Exception as exc:
            raise exception.FilterError(exc)
