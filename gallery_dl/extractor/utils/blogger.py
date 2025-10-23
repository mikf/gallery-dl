# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.


class BloggerAPI():
    """Minimal interface for the Blogger API v3

    https://developers.google.com/blogger
    """
    API_KEY = "AIzaSyCN9ax34oMMyM07g_M-5pjeDp_312eITK8"

    def __init__(self, extractor):
        self.extractor = extractor
        self.api_key = extractor.config("api-key") or self.API_KEY

    def blog_by_url(self, url):
        return self._call("/blogs/byurl", {"url": url}, "blog")

    def blog_posts(self, blog_id, label=None):
        endpoint = f"/blogs/{blog_id}/posts"
        params = {"labels": label}
        return self._pagination(endpoint, params)

    def blog_search(self, blog_id, query):
        endpoint = f"/blogs/{blog_id}/posts/search"
        params = {"q": query}
        return self._pagination(endpoint, params)

    def feeds_posts_default(self, blog, post):
        url = f"https://{blog}/feeds/posts/default/{post['id']}"
        params = {
            "alt"          : "json",
            "v"            : "2",
            "dynamicviews" : "1",
            "rewriteforssl": "true",
        }
        return self.extractor.request_json(url, params=params)

    def post_by_path(self, blog_id, path):
        endpoint = f"/blogs/{blog_id}/posts/bypath"
        return self._call(endpoint, {"path": path}, "post")

    def _call(self, endpoint, params, notfound=None):
        url = "https://www.googleapis.com/blogger/v3" + endpoint
        params["key"] = self.api_key
        return self.extractor.request_json(
            url, params=params, notfound=notfound)

    def _pagination(self, endpoint, params):
        while True:
            data = self._call(endpoint, params)
            if "items" in data:
                yield from data["items"]
            if "nextPageToken" not in data:
                return
            params["pageToken"] = data["nextPageToken"]
