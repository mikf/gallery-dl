# -*- coding: utf-8 -*-

# Copyright 2015-2018 Mike Fährmann
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
from .cache import cache


def request_func(self, *args, **kwargs):
    cookies = _cookiecache(self.root)
    if cookies:
        self.session.cookies.update(cookies)
    response = self.session.get(*args, **kwargs)
    if response.status_code == 503:
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
    url = text.urljoin(response.url, "/cdn-cgi/l/chk_jschl")
    return session.get(url, params=params)


def solve_jschl(url, page):
    """Solve challenge to get 'jschl_answer' value"""

    # build variable name
    # e.g. '...f, wqnVscP={"DERKbJk":+(...' --> wqnVscP.DERKbJk
    data, pos = text.extract_all(page, (
        ('var' , ',f, ', '='),
        ('key' , '"', '"'),
        ('expr', ':', '}'),
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
            # select arithmetc function based on operator (+, -, *)
            func = operator_functions[expr[vlength]]
            # evaluate the rest of the expression
            value = evaluate_expression(expr[vlength+2:])
            # combine the expression value with our current solution
            solution = func(solution, value)

        elif expr.startswith("a.value"):
            # add length of the hostname, i.e. add 11 for 'example.org'
            solution += len(urllib.parse.urlsplit(url).netloc)

            if ".toFixed(" in expr:
                # trim the solution to 10 decimal places
                # and strip trailing zeros
                solution = "{:.10f}".format(solution).rstrip("0")

            return solution


def evaluate_expression(expr, split_re=re.compile(r"\(+([^)]*)\)")):
    """Evaluate a Javascript expression for the challenge"""

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
            expression_values[part]
            for part in subexpr.split("[]")
        ))
    return int(result)


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
