# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Utility classes to setup OAuth"""

from .common import Extractor, Message
from . import reddit
import random
import socket
import string
import webbrowser
import urllib.parse


class OAuthBase(Extractor):
    category = "oauth"
    redirect_uri = "http://localhost:6414/"

    def __init__(self):
        Extractor.__init__(self)
        self.client = None

    def recv(self):
        print("Waiting for response. (Cancel with Ctrl+c)")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("localhost", 6414))
        server.listen(1)
        self.client = server.accept()[0]
        server.close()

        data = self.client.recv(1024).decode()
        path = data.split(" ", 2)[1]
        query = path.partition("?")[2]
        return {
            key: urllib.parse.unquote(value)
            for key, _, value in [
                part.partition("=")
                for part in query.split("&")
            ]
        }

    def send(self, msg):
        print(msg)
        self.client.send(b"HTTP/1.1 200 OK\r\n\r\n" + msg.encode())
        self.client.close()


class OAuthReddit(OAuthBase):
    subcategory = "reddit"
    pattern = ["oauth:reddit$"]

    def __init__(self, match):
        OAuthBase.__init__(self)
        self.session.headers["User-Agent"] = reddit.RedditAPI.USER_AGENT
        self.client_id = reddit.RedditAPI.CLIENT_ID
        self.state = "gallery-dl:{}:{}".format(
            self.subcategory,
            "".join(random.choice(string.ascii_letters) for _ in range(8)),
        )

    def items(self):
        yield Message.Version, 1

        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "state": self.state,
            "redirect_uri": self.redirect_uri,
            "duration": "permanent",
            "scope": "read",
        }
        url = "https://www.reddit.com/api/v1/authorize?"
        url += urllib.parse.urlencode(params)

        if not webbrowser.open(url):
            print("Please open this URL in your browser:")
            print(url, end="\n\n", flush=True)

        params = self.recv()

        if self.state != params.get("state"):
            self.send("'state' mismatch: expected {}, got {}.".format(
                      self.state, params.get("state")))
            return
        if "error" in params:
            self.send(params["error"])
            return

        url = "https://www.reddit.com/api/v1/access_token"
        data = {
            "grant_type": "authorization_code",
            "code": params["code"],
            "redirect_uri": self.redirect_uri,
        }
        response = self.session.post(url, data=data, auth=(self.client_id, ""))
        data = response.json()

        if "error" in data:
            self.send(data["error"])
        else:
            self.send(REDDIT_MSG_TEMPLATE.format(token=data["refresh_token"]))


REDDIT_MSG_TEMPLATE = """
Your Refresh Token is

{token}

Put this value into your configuration file as 'extractor.reddit.refesh-token'.

Example:
{{
    "extractor": {{
        "reddit": {{
            "refresh-token": "{token}"
        }}
    }}
}}
"""
