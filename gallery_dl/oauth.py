# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""OAuth helper functions and classes"""

import hmac
import time
import base64
import random
import string
import hashlib
import urllib.parse

import requests
import requests.auth

from . import text


class OAuth1Session(requests.Session):
    """Extension to requests.Session objects to support OAuth 1.0"""

    def __init__(self, consumer_key, consumer_secret,
                 token=None, token_secret=None):

        requests.Session.__init__(self)
        self.auth = OAuth1Client(
            consumer_key, consumer_secret,
            token, token_secret,
        )

    def rebuild_auth(self, prepared_request, response):
        if "Authorization" in prepared_request.headers:
            del prepared_request.headers["Authorization"]
            prepared_request.prepare_auth(self.auth)


class OAuth1Client(requests.auth.AuthBase):
    """OAuth1.0a authentication"""
    def __init__(self, consumer_key, consumer_secret,
                 token=None, token_secret=None):

        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.token = token
        self.token_secret = token_secret

    def __call__(self, request):
        oauth_params = [
            ("oauth_consumer_key", self.consumer_key),
            ("oauth_nonce", nonce(16)),
            ("oauth_signature_method", "HMAC-SHA1"),
            ("oauth_timestamp", str(int(time.time()))),
            ("oauth_version", "1.0"),
        ]
        if self.token:
            oauth_params.append(("oauth_token", self.token))

        signature = self.generate_signature(request, oauth_params)
        oauth_params.append(("oauth_signature", signature))

        request.headers["Authorization"] = "OAuth " + ",".join(
            key + '="' + value + '"' for key, value in oauth_params)

        return request

    def generate_signature(self, request, params):
        """Generate 'oauth_signature' value"""
        url, _, query = request.url.partition("?")

        params = params.copy()
        for key, value in text.parse_query(query).items():
            params.append((quote(key), quote(value)))
        params.sort()
        query = "&".join("=".join(item) for item in params)

        message = concat(request.method, url, query).encode()
        key = concat(self.consumer_secret, self.token_secret or "").encode()
        signature = hmac.new(key, message, hashlib.sha1).digest()

        return quote(base64.b64encode(signature).decode())


def concat(*args):
    """Concatenate 'args'"""
    return "&".join(quote(item) for item in args)


def nonce(size, alphabet=string.ascii_letters):
    """Generate a nonce value with 'size' characters"""
    return "".join(random.choice(alphabet) for _ in range(size))


def quote(value, quote=urllib.parse.quote):
    """Quote 'value' according to the OAuth1.0 standard"""
    return quote(value, "~")
