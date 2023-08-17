# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.2ch.hk/"""

from .common import Extractor, Message
from .. import text


class _2chThreadExtractor(Extractor):
    """Extractor for 2ch threads"""
    category = "2ch"
    subcategory = "thread"
    directory_fmt = ("{category}", "{board}", "{thread} {title}")
    filename_fmt = "{file_id} - {filename}.{extension}"
    archive_fmt = "{board}_{thread}_{file_id}"
    pattern = r"(?:https?://)?2ch\.hk/([^/]+)/res/(\d+)\.html"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.board, self.thread = match.groups()

    def items(self):
        url = f"https://2ch.hk/{self.board}/res/{self.thread}.json"
        thread_data = self.request(url).json()

        posts = thread_data["threads"][0]["posts"]
        post = posts[0]
        title = post.get("subject") or text.remove_html(post["comment"])

        thread_metadata = {
            "board": self.board,
            "thread": self.thread,
            "title": text.unescape(title)[:50],
        }

        yield Message.Directory, thread_metadata
        for post in posts:
            if "files" in post and post['files']:
                for file in post['files']:
                    file_metadata = {
                        "post_num": post["num"],
                        "file_id": file["name"].split('.')[0],
                        "filename": ".".join(file["fullname"].split('.')[:-1]),
                        "extension": file["name"].split('.')[-1],
                    }
                    file_metadata.update(thread_metadata)

                    url = f"https://2ch.hk/{file['path']}"
                    yield Message.Url, url, file_metadata


class _2chBoardExtractor(Extractor):
    """Extractor for 2ch boards"""
    category = "2ch"
    subcategory = "board"
    pattern = r"(?:https?://)?2ch\.hk/([a-z]+)/?$"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.board = match.group(1)

    def get_pages(self):
        url = f"https://2ch.hk/{self.board}/index.json"
        index_page = self.request(url).json()
        pages_total = len(index_page['pages'])

        yield index_page
        for i in range(1, pages_total):
            url = f"https://2ch.hk/{self.board}/{i}.json"
            yield self.request(url).json()

    def get_thread_nums(self):
        for page in self.get_pages():
            for thread in page["threads"]:
                yield thread["thread_num"]

    def items(self):
        for thread_num in self.get_thread_nums():
            url = f"https://2ch.hk/{self.board}/res/{thread_num}.html"
            yield Message.Queue, url, {"_extractor": _2chThreadExtractor}
