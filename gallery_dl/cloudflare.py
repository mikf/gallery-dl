# -*- coding: utf-8 -*-

# Copyright 2015-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Methods to access sites behind Cloudflare protection"""

import time
import operator
import collections
import urllib.parse
from xml.etree import ElementTree
from . import text
from .cache import memcache


def is_challenge(response):
    return (response.status_code == 503 and
            response.headers.get("Server", "").startswith("cloudflare") and
            b"jschl-answer" in response.content)


def is_captcha(response):
    return (response.status_code == 403 and
            b'name="captcha-bypass"' in response.content)


def solve_challenge(session, response, kwargs):
    """Solve Cloudflare challenge and get cfclearance cookie"""
    parsed = urllib.parse.urlsplit(response.url)
    root = parsed.scheme + "://" + parsed.netloc
    page = response.text

    cf_kwargs = {}
    headers = cf_kwargs["headers"] = collections.OrderedDict()
    params = cf_kwargs["data"] = collections.OrderedDict()
    headers["Referer"] = response.url

    form = text.extract(page, 'id="challenge-form"', '</form>')[0]
    for element in ElementTree.fromstring(
            "<f>" + form + "</f>").findall("input"):
        name = element.attrib.get("name")
        if not name:
            continue
        if name == "jschl_answer":
            try:
                value = solve_js_challenge(page, parsed.netloc)
            except Exception:
                return response, None, None
        else:
            value = element.attrib.get("value")
        params[name] = value

    try:
        params = {"ray": text.extract(page, '?ray=', '"')[0]}

        url = root + "/cdn-cgi/images/trace/jschal/nojs/transparent.gif"
        session.request("GET", url, params=params)

        url = root + "/cdn-cgi/images/trace/jschal/js/nocookie/transparent.gif"
        session.request("GET", url, params=params)
    except Exception:
        pass

    time.sleep(4)
    url = root + text.unescape(text.extract(page, 'action="', '"')[0])
    cf_response = session.request("POST", url, **cf_kwargs)

    if cf_response.history:
        initial_response = cf_response.history[0]
    else:
        initial_response = cf_response

    cookies = {
        cookie.name: cookie.value
        for cookie in initial_response.cookies
    }

    if not cookies:
        import logging
        log = logging.getLogger("cloudflare")
        log.debug("Headers:\n%s", initial_response.headers)
        log.debug("Content:\n%s", initial_response.text)
        return cf_response, None, None

    domain = next(iter(initial_response.cookies)).domain
    cookies["__cfduid"] = response.cookies.get("__cfduid", "")
    return cf_response, domain, cookies


def solve_js_challenge(page, netloc):
    """Evaluate JS challenge in 'page' to get 'jschl_answer' value"""

    # build variable name
    # e.g. '...f, wqnVscP={"DERKbJk":+(...' --> wqnVscP.DERKbJk
    data, pos = text.extract_all(page, (
        ('var' , ',f, ', '='),
        ('key' , '"'   , '"'),
        ('expr', ':'   , '}'),
    ))
    variable = "{}.{}".format(data["var"], data["key"])
    vlength = len(variable)

    k = text.extract(page, "k = '", "'")[0]

    # evaluate the initial expression
    solution = evaluate_expression(data["expr"], page, netloc)

    # iterator over all remaining expressions
    # and combine their values in 'solution'
    expressions = text.extract(
        page, "'challenge-form');", "f.submit();", pos)[0]
    for expr in expressions.split(";")[1:]:

        if expr.startswith(variable):
            # select arithmetc function based on operator (+/-/*)
            func = OPERATORS[expr[vlength]]
            # evaluate the rest of the expression
            value = evaluate_expression(expr[vlength+2:], page, netloc, k)
            # combine expression value with our current solution
            solution = func(solution, value)

        elif expr.startswith("a.value"):
            if "t.length)" in expr:
                # add length of hostname
                solution += len(netloc)
            if ".toFixed(" in expr:
                # trim solution to 10 decimal places
                solution = "{:.10f}".format(solution)
            return solution

        elif expr.startswith("k+="):
            k += str(evaluate_expression(expr[3:], page, netloc))


def evaluate_expression(expr, page, netloc, k=""):
    """Evaluate a single Javascript expression for the challenge"""

    if expr.startswith("function(p)"):
        # get HTML element with ID k and evaluate the expression inside
        # 'eval(eval("document.getElementById(k).innerHTML"))'
        expr = text.extract(page, 'id="'+k+'"', '<')[0]
        return evaluate_expression(expr.partition(">")[2], page, netloc)

    if "/" in expr:
        # split the expression in numerator and denominator subexpressions,
        # evaluate them separately,
        # and return their fraction-result
        num, _, denom = expr.partition("/")
        num = evaluate_expression(num, page, netloc)
        denom = evaluate_expression(denom, page, netloc)
        return num / denom

    if "function(p)" in expr:
        # split initial expression and function code
        initial, _, func = expr.partition("function(p)")
        # evaluate said expression
        initial = evaluate_expression(initial, page, netloc)
        # get function argument and use it as index into 'netloc'
        index = evaluate_expression(func[func.index("}")+1:], page, netloc)
        return initial + ord(netloc[int(index)])

    # iterate over all subexpressions,
    # evaluate them,
    # and accumulate their values in 'result'
    result = ""
    for subexpr in expr.strip("+()").split(")+("):
        value = 0
        for part in subexpr.split("+"):
            if "-" in part:
                p1, _, p2 = part.partition("-")
                value += VALUES[p1] - VALUES[p2]
            else:
                value += VALUES[part]
        result += str(value)
    return int(result)


OPERATORS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
}


VALUES = {
    "": 0,
    "!": 1,
    "[]": 0,
    "!![]": 1,
    "(!![]": 1,
    "(!![])": 1,
}


@memcache(keyarg=0)
def cookies(category):
    return None
