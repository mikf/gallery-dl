# -*- coding: utf-8 -*-

# Copyright 2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://kemono.party/"""

from .common import Extractor, Message
from .. import text
import re


class KemonopartyExtractor(Extractor):
    """Base class for kemonoparty extractors"""
    category = "kemonoparty"
    root = "https://kemono.party"
    directory_fmt = ("{category}", "{user_id}")
    filename_fmt = "{post_id}_{title}_{filename}.{extension}"
    archive_fmt = "{user_id}_{post_id}_{filename}.{extension}"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.file_re = re.compile(r'href="(/(?:file|attachment)s/[^"]+)')

    def items(self):
        for post_url in self.posts():
            try:
                post = self._parse_post(post_url)
            except Exception:
                self.log.warning("Error while parsing %s", post_url)
                self.log.debug("", exc_info=True)
                continue

            files = post.pop("_files")
            yield Message.Directory, post
            for num, file in enumerate(files, 1):
                file.update(post)
                file["num"] = num
                url = file["url"]
                yield Message.Url, url, text.nameext_from_url(url, file)

    def _parse_post(self, url):
        page = self.request(url).text
        _, _, _, service, _, user_id, _, post_id = url.split("/")

        published, pos = text.extract(page, 'name="published" content="', '"')
        pos = page.index('id="page"', pos)
        files = [
            {"url": self.root + path}
            for path in self.file_re.findall(page, pos)
        ]
        title  , pos = text.extract(page, "<h1>", "</h1>", pos)
        content, pos = text.extract(page, "<p>", "</p>\n ", pos)

        return {
            "service": service,
            "user_id": text.parse_int(user_id),
            "post_id": text.parse_int(post_id),
            "title"  : text.unescape(title),
            "content": content,
            "date"   : text.parse_datetime(published, "%Y-%m-%d %H:%M:%S"),
            "_files" : files,
        }


class KemonopartyUserExtractor(KemonopartyExtractor):
    """Extractor for all posts from a kemono.party user listing"""
    subcategory = "user"
    pattern = r"(?:https?://)?kemono\.party/([^/?#]+)/user/(\d+)/?(?:$|[?#])"
    test = ("https://kemono.party/fanbox/user/6993449", {
        "range": "1-25",
        "count": 25,
    })

    def __init__(self, match):
        KemonopartyExtractor.__init__(self, match)
        service, user_id = match.groups()
        self.path = "/{}/user/{}".format(service, user_id)

    def posts(self):
        needle = 'href="' + self.path + "/post/"
        url = self.root + self.path
        params = {"o": 0}

        while True:
            page = self.request(url, params=params).text

            cnt = 0
            for post_id in text.extract_iter(page, needle, '"'):
                cnt += 1
                yield url + "/post/" + post_id

            if cnt < 25:
                return
            params["o"] += 25


class KemonopartyPostExtractor(KemonopartyExtractor):
    """Extractor for a single kemono.party post"""
    subcategory = "post"
    pattern = r"(?:https?://)?kemono\.party/([^/?#]+)/user/(\d+)/post/(\d+)"
    test = ("https://kemono.party/fanbox/user/6993449/post/506575", {
        "url": "e8969211ba4382aa33ec68f72dd4aa00cfeefd1b",
        "keyword": "54a4852eaad694a69dcd9e8dd4670de8b20d6f38",
    })

    def __init__(self, match):
        KemonopartyExtractor.__init__(self, match)
        service, user_id, post_id = match.groups()
        self.post_url = "{}/{}/user/{}/post/{}".format(
            self.root, service, user_id, post_id)

    def posts(self):
        return (self.post_url,)
