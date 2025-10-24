# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import text, util, exception


class BilibiliAPI():
    def __init__(self, extractor):
        self.extractor = extractor

    def _call(self, endpoint, params):
        url = "https://api.bilibili.com/x/polymer/web-dynamic/v1" + endpoint
        data = self.extractor.request_json(url, params=params)

        if data["code"]:
            self.extractor.log.debug("Server response: %s", data)
            raise exception.AbortExtraction("API request failed")

        return data

    def user_articles(self, user_id):
        endpoint = "/opus/feed/space"
        params = {"host_mid": user_id}

        while True:
            data = self._call(endpoint, params)

            for item in data["data"]["items"]:
                params["offset"] = item["opus_id"]
                yield item

            if not data["data"]["has_more"]:
                break

    def article(self, article_id):
        url = "https://www.bilibili.com/opus/" + article_id

        while True:
            page = self.extractor.request(url).text
            try:
                return util.json_loads(text.extr(
                    page, "window.__INITIAL_STATE__=", "};") + "}")
            except Exception:
                if "window._riskdata_" not in page:
                    raise exception.AbortExtraction(
                        f"{article_id}: Unable to extract INITIAL_STATE data")
            self.extractor.wait(seconds=300)

    def user_favlist(self):
        endpoint = "/opus/feed/fav"
        params = {"page": 1, "page_size": 20}

        while True:
            data = self._call(endpoint, params)["data"]

            yield from data["items"]

            if not data.get("has_more"):
                break
            params["page"] += 1

    def login_user_id(self):
        url = "https://api.bilibili.com/x/space/v2/myinfo"
        data = self.extractor.request_json(url)

        if data["code"] != 0:
            self.extractor.log.debug("Server response: %s", data)
            raise exception.AbortExtraction(
                "API request failed. Are you logges in?")
        try:
            return data["data"]["profile"]["mid"]
        except Exception:
            raise exception.AbortExtraction("API request failed")
