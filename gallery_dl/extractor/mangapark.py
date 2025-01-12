# -*- coding: utf-8 -*-

# Copyright 2015-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://mangapark.net/"""

from .common import ChapterExtractor, Extractor, Message
from .. import text, util, exception
import re

BASE_PATTERN = r"(?:https?://)?(?:www\.)?mangapark\.(?:net|com|org|io|me)"


class MangaparkBase():
    """Base class for mangapark extractors"""
    category = "mangapark"
    _match_title = None

    def _parse_chapter_title(self, title):
        if not self._match_title:
            MangaparkBase._match_title = re.compile(
                r"(?i)"
                r"(?:vol(?:\.|ume)?\s*(\d+)\s*)?"
                r"ch(?:\.|apter)?\s*(\d+)([^\s:]*)"
                r"(?:\s*:\s*(.*))?"
            ).match
        match = self._match_title(title)
        return match.groups() if match else (0, 0, "", "")


class MangaparkChapterExtractor(MangaparkBase, ChapterExtractor):
    """Extractor for manga-chapters from mangapark.net"""
    pattern = BASE_PATTERN + r"/title/[^/?#]+/(\d+)"
    example = "https://mangapark.net/title/MANGA/12345-en-ch.01"

    def __init__(self, match):
        self.root = text.root_from_url(match.group(0))
        url = "{}/title/_/{}".format(self.root, match.group(1))
        ChapterExtractor.__init__(self, match, url)

    def metadata(self, page):
        data = self._extract_nextdata(page)
        chapter = (data["props"]["pageProps"]["dehydratedState"]
                   ["queries"][0]["state"]["data"]["data"])
        manga = chapter["comicNode"]["data"]
        source = chapter["sourceNode"]["data"]

        self._urls = chapter["imageSet"]["httpLis"]
        self._params = chapter["imageSet"]["wordLis"]
        vol, ch, minor, title = self._parse_chapter_title(chapter["dname"])

        return {
            "manga"     : manga["name"],
            "manga_id"  : manga["id"],
            "artist"    : source["artists"],
            "author"    : source["authors"],
            "genre"     : source["genres"],
            "volume"    : text.parse_int(vol),
            "chapter"   : text.parse_int(ch),
            "chapter_minor": minor,
            "chapter_id": chapter["id"],
            "title"     : chapter["title"] or title or "",
            "lang"      : chapter["lang"],
            "language"  : util.code_to_language(chapter["lang"]),
            "source"    : source["srcTitle"],
            "source_id" : source["id"],
            "date"      : text.parse_timestamp(chapter["dateCreate"] // 1000),
        }

    def images(self, page):
        return [
            (url + "?" + params, None)
            for url, params in zip(self._urls, self._params)
        ]


class MangaparkMangaExtractor(MangaparkBase, Extractor):
    """Extractor for manga from mangapark.net"""
    subcategory = "manga"
    pattern = BASE_PATTERN + r"/title/(\d+)(?:-[^/?#]*)?/?$"
    example = "https://mangapark.net/title/12345-MANGA"

    def __init__(self, match):
        self.root = text.root_from_url(match.group(0))
        self.manga_id = int(match.group(1))
        Extractor.__init__(self, match)

    def items(self):
        for chapter in self.chapters():
            chapter = chapter["data"]
            url = self.root + chapter["urlPath"]

            vol, ch, minor, title = self._parse_chapter_title(chapter["dname"])
            data = {
                "manga_id"  : self.manga_id,
                "volume"    : text.parse_int(vol),
                "chapter"   : text.parse_int(ch),
                "chapter_minor": minor,
                "chapter_id": chapter["id"],
                "title"     : chapter["title"] or title or "",
                "lang"      : chapter["lang"],
                "language"  : util.code_to_language(chapter["lang"]),
                "source"    : chapter["srcTitle"],
                "source_id" : chapter["sourceId"],
                "date"      : text.parse_timestamp(
                    chapter["dateCreate"] // 1000),
                "_extractor": MangaparkChapterExtractor,
            }
            yield Message.Queue, url, data

    def chapters(self):
        source = self.config("source")
        if not source:
            return self.chapters_all()

        source_id = self._select_source(source)
        self.log.debug("Requesting chapters for source_id %s", source_id)
        return self.chapters_source(source_id)

    def chapters_all(self):
        pnum = 0
        variables = {
            "select": {
                "comicId": self.manga_id,
                "range"  : None,
                "isAsc"  : not self.config("chapter-reverse"),
            }
        }

        while True:
            data = self._request_graphql(
                "get_content_comicChapterRangeList", variables)

            for item in data["items"]:
                yield from item["chapterNodes"]

            if not pnum:
                pager = data["pager"]
            pnum += 1

            try:
                variables["select"]["range"] = pager[pnum]
            except IndexError:
                return

    def chapters_source(self, source_id):
        variables = {
            "sourceId": source_id,
        }
        chapters = self._request_graphql(
            "get_content_source_chapterList", variables)

        if self.config("chapter-reverse"):
            chapters.reverse()
        return chapters

    def _select_source(self, source):
        if isinstance(source, int):
            return source

        group, _, lang = source.partition(":")
        group = group.lower()

        variables = {
            "comicId"    : self.manga_id,
            "dbStatuss"  : ["normal"],
            "haveChapter": True,
        }
        for item in self._request_graphql(
                "get_content_comic_sources", variables):
            data = item["data"]
            if (not group or data["srcTitle"].lower() == group) and (
                    not lang or data["lang"] == lang):
                return data["id"]

        raise exception.StopExtraction(
            "'%s' does not match any available source", source)

    def _request_graphql(self, opname, variables):
        url = self.root + "/apo/"
        data = {
            "query"        : QUERIES[opname],
            "variables"    : util.json_dumps(variables),
            "operationName": opname,
        }
        return self.request(
            url, method="POST", json=data).json()["data"][opname]


QUERIES = {
    "get_content_comicChapterRangeList": """
  query get_content_comicChapterRangeList($select: Content_ComicChapterRangeList_Select) {
    get_content_comicChapterRangeList(
      select: $select
    ) {
      reqRange{x y}
      missing
      pager {x y}
      items{
        serial
        chapterNodes {

  id
  data {


  id
  sourceId

  dbStatus
  isNormal
  isHidden
  isDeleted
  isFinal

  dateCreate
  datePublic
  dateModify
  lang
  volume
  serial
  dname
  title
  urlPath

  srcTitle srcColor

  count_images

  stat_count_post_child
  stat_count_post_reply
  stat_count_views_login
  stat_count_views_guest

  userId
  userNode {

  id
  data {

id
name
uniq
avatarUrl
urlPath

verified
deleted
banned

dateCreate
dateOnline

stat_count_chapters_normal
stat_count_chapters_others

is_adm is_mod is_vip is_upr

  }

  }

  disqusId


  }

          sser_read
        }
      }

    }
  }
""",

    "get_content_source_chapterList": """
  query get_content_source_chapterList($sourceId: Int!) {
    get_content_source_chapterList(
      sourceId: $sourceId
    ) {

  id
  data {


  id
  sourceId

  dbStatus
  isNormal
  isHidden
  isDeleted
  isFinal

  dateCreate
  datePublic
  dateModify
  lang
  volume
  serial
  dname
  title
  urlPath

  srcTitle srcColor

  count_images

  stat_count_post_child
  stat_count_post_reply
  stat_count_views_login
  stat_count_views_guest

  userId
  userNode {

  id
  data {

id
name
uniq
avatarUrl
urlPath

verified
deleted
banned

dateCreate
dateOnline

stat_count_chapters_normal
stat_count_chapters_others

is_adm is_mod is_vip is_upr

  }

  }

  disqusId


  }

    }
  }
""",

    "get_content_comic_sources": """
  query get_content_comic_sources($comicId: Int!, $dbStatuss: [String] = [], $userId: Int, $haveChapter: Boolean, $sortFor: String) {
    get_content_comic_sources(
      comicId: $comicId
      dbStatuss: $dbStatuss
      userId: $userId
      haveChapter: $haveChapter
      sortFor: $sortFor
    ) {

id
data{

  id

  dbStatus
  isNormal
  isHidden
  isDeleted

  lang name altNames authors artists

  release
  genres summary{code} extraInfo{code}

  urlCover600
  urlCover300
  urlCoverOri

  srcTitle srcColor

  chapterCount
  chapterNode_last {
    id
    data {
      dateCreate datePublic dateModify
      volume serial
      dname title
      urlPath
      userNode {
        id data {uniq name}
      }
    }
  }
}

    }
  }
""",
}
