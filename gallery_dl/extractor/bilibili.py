# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.bilibili.com/"""

from .common import Extractor, Message
from .. import text


class BilibiliExtractor(Extractor):
    """Base class for bilibili extractors"""
    category = "bilibili"
    root = "https://www.bilibili.com"
    request_interval = (3.0, 6.0)

    def _init(self):
        self.api = self.utils().BilibiliAPI(self)

    def items(self):
        for article in self.articles():
            article["_extractor"] = BilibiliArticleExtractor
            url = f"{self.root}/opus/{article['opus_id']}"
            yield Message.Queue, url, article


class BilibiliArticleExtractor(BilibiliExtractor):
    """Extractor for a bilibili article"""
    subcategory = "article"
    pattern = (r"(?:https?://)?"
               r"(?:t\.bilibili\.com|(?:www\.)?bilibili.com/opus)/(\d+)")
    example = "https://www.bilibili.com/opus/12345"
    directory_fmt = ("{category}", "{username}")
    filename_fmt = "{id}_{num}.{extension}"
    archive_fmt = "{id}_{num}"

    def items(self):
        article_id = self.groups[0]
        article = self.api.article(article_id)

        # Flatten modules list
        modules = {}
        for module in article["detail"]["modules"]:
            if module["module_type"] == "MODULE_TYPE_BLOCKED":
                self.log.warning("%s: Blocked Article\n%s", article_id,
                                 module["module_blocked"].get("hint_message"))
            del module["module_type"]
            modules.update(module)
        article["detail"]["modules"] = modules

        article["username"] = modules["module_author"]["name"]

        pics = []

        if "module_top" in modules:
            try:
                pics.extend(modules["module_top"]["display"]["album"]["pics"])
            except Exception:
                pass

        if "module_content" in modules:
            for paragraph in modules["module_content"]["paragraphs"]:
                if "pic" not in paragraph:
                    continue

                try:
                    pics.extend(paragraph["pic"]["pics"])
                except Exception:
                    pass

        article["count"] = len(pics)
        yield Message.Directory, article
        for article["num"], pic in enumerate(pics, 1):
            url = pic["url"]
            article.update(pic)
            yield Message.Url, url, text.nameext_from_url(url, article)


class BilibiliUserArticlesExtractor(BilibiliExtractor):
    """Extractor for a bilibili user's articles"""
    subcategory = "user-articles"
    pattern = (r"(?:https?://)?space\.bilibili\.com/(\d+)"
               r"/(?:article|upload/opus)")
    example = "https://space.bilibili.com/12345/article"

    def articles(self):
        return self.api.user_articles(self.groups[0])


class BilibiliUserArticlesFavoriteExtractor(BilibiliExtractor):
    subcategory = "user-articles-favorite"
    pattern = (r"(?:https?://)?space\.bilibili\.com"
               r"/(\d+)/favlist\?fid=opus")
    example = "https://space.bilibili.com/12345/favlist?fid=opus"
    _warning = True

    def articles(self):
        if self._warning:
            if not self.cookies_check(("SESSDATA",)):
                self.log.error("'SESSDATA' cookie required")
            BilibiliUserArticlesFavoriteExtractor._warning = False
        return self.api.user_favlist()
