# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Utility classes for OAuth 1.0"""

import hmac
import time
import base64
import random
import string
import hashlib
import urllib.parse


class OAuthSession():
    """Minimal wrapper for requests.session objects to support OAuth 1.0"""
    def __init__(self, session, consumer_key, consumer_secret,
                 token=None, token_secret=None):
        self.session = session
        self.consumer_secret = consumer_secret
        self.token_secret = token_secret or ""
        self.params = session.params
        self.params["oauth_consumer_key"] = consumer_key
        self.params["oauth_token"] = token
        self.params["oauth_signature_method"] = "HMAC-SHA1"
        self.params["oauth_version"] = "1.0"

    def get(self, url, params):
        params.update(self.params)
        params["oauth_nonce"] = self.nonce(16)
        params["oauth_timestamp"] = int(time.time())
        params["oauth_signature"] = self.signature(url, params)
        return self.session.get(url, params=params)

    def signature(self, url, params):
        """Generate 'oauth_signature' value"""
        query = urllib.parse.urlencode(sorted(params.items()))
        message = self.concat("GET", url, query).encode()
        key = self.concat(self.consumer_secret, self.token_secret).encode()
        signature = hmac.new(key, message, hashlib.sha1).digest()
        return base64.b64encode(signature).decode()

    @staticmethod
    def concat(*args):
        return "&".join(urllib.parse.quote(item, "") for item in args)

    @staticmethod
    def nonce(N, alphabet=string.ascii_letters):
        return "".join(random.choice(alphabet) for _ in range(N))
