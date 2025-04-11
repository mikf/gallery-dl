# -*- coding: utf-8 -*-

# Copyright 2015-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://mangapark.net/"""

from .common import ChapterExtractor, Extractor, Message
from .. import text, util, exception
from ..cache import memcache
import re

BASE_PATTERN = (r"(?:https?://)?(?:www\.)?(?:"
                r"(?:manga|comic|read)park\.(?:com|net|org|me|io|to)|"
                r"parkmanga\.(?:com|net|org)|"
                r"mpark\.to)")


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

    @memcache(keyarg=1)
    def _extract_manga(self, manga_id):
        variables = {
            "getComicNodeId": manga_id,
        }
        return self._request_graphql("Get_comicNode", variables)["data"]

    def _extract_chapter(self, chapter_id):
        variables = {
            "getChapterNodeId": chapter_id,
        }
        return self._request_graphql("Get_chapterNode", variables)["data"]

    def _extract_chapters_all(self, manga_id):
        variables = {
            "comicId": manga_id,
        }
        return self._request_graphql("Get_comicChapterList", variables)

    def _extract_chapters_source(self, source_id):
        variables = {
            "sourceId": source_id,
        }
        return self._request_graphql(
            "get_content_source_chapterList", variables)

    def _request_graphql(self, opname, variables):
        url = self.root + "/apo/"
        data = {
            "query"        : QUERIES[opname],
            "variables"    : variables,
            "operationName": opname,
        }
        return self.request(
            url, method="POST", json=data).json()["data"].popitem()[1]


class MangaparkChapterExtractor(MangaparkBase, ChapterExtractor):
    """Extractor for manga-chapters from mangapark.net"""
    pattern = (BASE_PATTERN +
               r"/(?:title/[^/?#]+/|comic/\d+/[^/?#]+/[^/?#]+-i)(\d+)")
    example = "https://mangapark.net/title/MANGA/12345-en-ch.01"

    def __init__(self, match):
        self.root = text.root_from_url(match.group(0))
        ChapterExtractor.__init__(self, match, False)

    def metadata(self, _):
        chapter = self._extract_chapter(self.groups[0])
        manga = self._extract_manga(chapter["comicNode"]["id"])

        self._urls = chapter["imageFile"]["urlList"]
        vol, ch, minor, title = self._parse_chapter_title(chapter["dname"])
        lang = chapter.get("lang") or "en"

        return {
            "manga"     : manga["name"],
            "manga_id"  : text.parse_int(manga["id"]),
            "artist"    : manga["artists"],
            "author"    : manga["authors"],
            "genre"     : manga["genres"],
            "volume"    : text.parse_int(vol),
            "chapter"   : text.parse_int(ch),
            "chapter_minor": minor,
            "chapter_id": text.parse_int(chapter["id"]),
            "title"     : title or "",
            "lang"      : lang,
            "language"  : util.code_to_language(lang),
            "source"    : chapter["srcTitle"],
            "source_id" : chapter["sourceId"],
            "date"      : text.parse_timestamp(chapter["dateCreate"] // 1000),
        }

    def images(self, _):
        return [(url, None) for url in self._urls]


class MangaparkMangaExtractor(MangaparkBase, Extractor):
    """Extractor for manga from mangapark.net"""
    subcategory = "manga"
    pattern = BASE_PATTERN + r"/(?:title|comic)/(\d+)(?:[/-][^/?#]*)?/?$"
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
            lang = chapter.get("lang") or "en"

            data = {
                "manga_id"  : self.manga_id,
                "volume"    : text.parse_int(vol),
                "chapter"   : text.parse_int(ch),
                "chapter_minor": minor,
                "chapter_id": chapter["id"],
                "title"     : chapter["title"] or title or "",
                "lang"      : lang,
                "language"  : util.code_to_language(lang),
                "source"    : chapter["srcTitle"],
                "source_id" : chapter["sourceId"],
                "date"      : text.parse_timestamp(
                    chapter["dateCreate"] // 1000),
                "_extractor": MangaparkChapterExtractor,
            }
            yield Message.Queue, url, data

    def chapters(self):
        source = self.config("source")
        if source:
            source_id = self._select_source(source)
            self.log.debug("Requesting chapters for source_id %s", source_id)
            chapters = self._extract_chapters_source(source_id)
        else:
            chapters = self._extract_chapters_all(self.groups[0])

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


QUERIES = {
    "Get_comicChapterList": """
query Get_comicChapterList($comicId: ID!) {
    get_comicChapterList(comicId: $comicId) {
        data {
            id
            dname
            title
            lang
            urlPath
            srcTitle
            sourceId
            dateCreate
        }
    }
}
""",

    "Get_chapterNode": """
query Get_chapterNode($getChapterNodeId: ID!) {
    get_chapterNode(id: $getChapterNodeId) {
        data {
            id
            dname
            lang
            sourceId
            srcTitle
            dateCreate
            comicNode{
                id
            }
            imageFile {
                urlList
            }
        }
    }
}
""",

    "Get_comicNode": """
query Get_comicNode($getComicNodeId: ID!) {
    get_comicNode(id: $getComicNodeId) {
        data {
            id
            name
            artists
            authors
            genres
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
