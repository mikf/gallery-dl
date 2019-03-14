# -*- coding: utf-8 -*-

# Copyright 2015-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Methods to access sites behind Cloudflare protection"""

import re
import time
import operator
import urllib.parse
from . import text
from .cache import memcache


def is_challenge(response):
    return (response.status_code == 503 and
            response.headers.get("Server", "").startswith("cloudflare") and
            b"jschl-answer" in response.content)


def solve_challenge(session, response, kwargs):
    """Solve Cloudflare challenge and get cfclearance cookie"""
    parsed = urllib.parse.urlsplit(response.url)
    root = parsed.scheme + "://" + parsed.netloc

    cf_kwargs = kwargs.copy()
    headers = cf_kwargs["headers"] = (
        kwargs["headers"].copy() if "headers" in kwargs else {})
    params = cf_kwargs["params"] = (
        kwargs["params"].copy() if "params" in kwargs else {})

    page = response.text
    params["pass"] = text.extract(page, 'name="pass" value="', '"')[0]
    params["jschl_vc"] = text.extract(page, 'name="jschl_vc" value="', '"')[0]
    params["jschl_answer"] = solve_js_challenge(page, parsed.netloc)
    headers["Referer"] = response.url

    time.sleep(4)

    url = root + "/cdn-cgi/l/chk_jschl"
    cf_kwargs["allow_redirects"] = False
    cf_response = session.request(response.request.method, url, **cf_kwargs)

    location = cf_response.headers["Location"]
    if location[0] == "/":
        location = root + location

    for cookie in cf_response.cookies:
        if cookie.name == "cf_clearance":
            return location, cookie.domain, {
                cookie.name: cookie.value,
                "__cfduid" : response.cookies.get("__cfduid", ""),
            }
    return location, "", {}


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

    # evaluate the initial expression
    solution = evaluate_expression(data["expr"])

    # iterator over all remaining expressions
    # and combine their values in 'solution'
    expressions = text.extract(
        page, "'challenge-form');", "f.submit();", pos)[0]
    for expr in expressions.split(";")[1:]:

        if expr.startswith(variable):
            # select arithmetc function based on operator (+/-/*)
            func = OPERATORS[expr[vlength]]
            # evaluate the rest of the expression
            value = evaluate_expression(expr[vlength+2:])
            # combine expression value with our current solution
            solution = func(solution, value)

        elif expr.startswith("a.value"):
            # add length of hostname
            solution += len(netloc)

            if ".toFixed(" in expr:
                # trim solution to 10 decimal places
                # and strip trailing zeros
                solution = "{:.10f}".format(solution).rstrip("0")

            return solution


def evaluate_expression(expr, split_re=re.compile(r"\(+([^)]*)\)")):
    """Evaluate a single Javascript expression for the challenge"""

    if "/" in expr:
        # split the expression in numerator and denominator subexpressions,
        # evaluate them separately,
        # and return their fraction-result
        num, _, denom = expr.partition("/")
        return evaluate_expression(num) / evaluate_expression(denom)

    # iterate over all subexpressions,
    # evaluate them,
    # and accumulate their values in 'result'
    result = ""
    for subexpr in split_re.findall(expr):
        result += str(sum(
            VALUES[part]
            for part in subexpr.split("[]")
        ))
    return int(result)


OPERATORS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
}

VALUES = {
    "": 0,
    "+": 0,
    "!+": 1,
    "+!!": 1,
}


@memcache(keyarg=0)
def cookies(category):
    return None
