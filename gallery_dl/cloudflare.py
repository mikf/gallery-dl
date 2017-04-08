# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Methods to access sites behind Cloudflare protection"""

import time
import operator
import urllib.parse
from . import text
from .cache import cache


def request_func(self, *args):
    cookies = _cookiecache(self.root)
    if cookies:
        self.session.cookies = cookies
    response = self.session.get(*args)
    if response.status_code != 200:
        _cookiecache.invalidate(self.root)
        self.log.debug(response.text)
        self.log.info("Solving Cloudflare challenge")
        response = solve_challenge(self.session, response)
        _cookiecache(self.root, self.session.cookies)
    return response


def solve_challenge(session, response):
    session.headers["Referer"] = response.url
    page = response.text
    params = text.extract_all(page, (
        ('jschl_vc', 'name="jschl_vc" value="', '"'),
        ('pass'    , 'name="pass" value="', '"'),
    ))[0]
    params["jschl_answer"] = solve_jschl(response.url, page)
    time.sleep(4)
    url = urllib.parse.urljoin(response.url, "/cdn-cgi/l/chk_jschl")
    return session.get(url, params=params)


def solve_jschl(url, page):
    """Solve challenge to get 'jschl_answer' value"""
    data, pos = text.extract_all(page, (
        ('var' , ',f, ', '='),
        ('key' , '"', '"'),
        ('expr', ':', '}'),
    ))
    solution = evaluate_expression(data["expr"])
    variable = "{}.{}".format(data["var"], data["key"])
    vlength = len(variable)
    expressions = text.extract(
        page, "'challenge-form');", "f.submit();", pos
    )[0]
    for expr in expressions.split(";")[1:]:
        if expr.startswith(variable):
            func = operator_functions[expr[vlength]]
            value = evaluate_expression(expr[vlength+2:])
            solution = func(solution, value)
        elif expr.startswith("a.value"):
            return solution + len(urllib.parse.urlsplit(url).netloc)


def evaluate_expression(expr):
    """Evaluate a Javascript expression for the challenge"""
    stack = []
    ranges = []
    value = ""
    for index, char in enumerate(expr):
        if char == "(":
            stack.append(index+1)
        elif char == ")":
            begin = stack.pop()
            if stack:
                ranges.append((begin, index))
    for subexpr in [expr[begin:end] for begin, end in ranges] or (expr,):
        num = 0
        for part in subexpr.split("[]"):
            num += expression_values[part]
        value += str(num)
    return int(value)


operator_functions = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
}

expression_values = {
    "": 0,
    "+": 0,
    "!+": 1,
    "+!!": 1,
}


@cache(maxage=365*24*60*60, keyarg=0)
def _cookiecache(key, item=None):
    return item
