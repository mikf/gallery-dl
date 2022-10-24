# -*- coding: utf-8 -*-

# Copyright 2021 Seonghyeon Cho
# Copyright 2022 Mike Fährmann
# Copyright 2022 Ronsor Labs
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://ac.qq.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text
import base64, json, re

BASE_PATTERN = (r"(?:https?://)?ac\.qq\.com"
                r"/(Comic/[cC]omicInfo/id|ComicView/index/id)/([0-9]+)")


class AcqqBase():
    """Base class for tencent comics extractors"""
    category = "acqq"
    root = "https://ac.qq.com"

class AcqqChapterExtractor(AcqqBase, GalleryExtractor):
    subcategory = "chapter"
    directory_fmt = ("{category}", "{comic}")
    filename_fmt = "{chapter:>03}-{num:>02}.{extension}"
    archive_fmt = "{comic_id}_{chapter}_{num}"
    pattern = BASE_PATTERN + r"/cid/([0-9]+)"
    test = (
        (("https://ac.qq.com/ComicView/index/id/650205/cid/1917"), {
            "url": "7ffd00cb1e6914aba91252cd94b88c163405aebf",
            "count": 15
        }),
        (("https://ac.qq.com/ComicView/index/id/651642/cid/1697"), {
            "count": "84"
        })
    )

    def __init__(self, match):
        path, comic_id, chapter_id = match.groups()
        url = "{}/{}/{}/cid/{}".format(self.root, path, comic_id, chapter_id)
        GalleryExtractor.__init__(self, match, url)

        self.comic_id = comic_id
        self.chapter_id = chapter_id

    def metadata(self, page):
        data = AcqqChapterExtractor._extract_data(page)
        return {
            "comic_id": self.comic_id,
            "chapter_id": self.chapter_id,
            "chapter" : data['chapter']['cSeq'],
            "title"   : data['chapter']['cTitle'],
            "comic"   : data['comic']['title'],
            "description": text.extract(page, '\u300b\u7b80\u4ecb\uff1a', '"'),
            "artist"  : data['artist']['nick'],
        }

    @staticmethod
    def images(page):
        data = AcqqChapterExtractor._extract_data(page)
        return [
            (picture['url'], None)
            for picture in data['picture']
        ]

    @staticmethod
    def _extract_data(page):
        data_enc = text.extract(page, "DATA = '", "'")[0]
        nonce_expr = re.findall(AcqqChapterExtractor.nonce_decl_pattern, page)[0]
        nonce = AcqqChapterExtractor._eval_js_expr(nonce_expr)
        return json.loads(AcqqChapterExtractor._decode_chapter_data(data_enc, nonce))

    nonce_decl_pattern = r"window.*n.*o.*n.*c.*e.*= ([^'].*);"
    @staticmethod
    def _decrypt_with_nonce(blob, nonce):
      """Decrypt a blob of data given the correct nonce"""
      arr = list(blob.strip())
      mtc = re.findall(r'(\d+[a-zA-Z]+)', nonce)
      mtc.reverse()
      for v in mtc:
        off = int(re.match(r'\d+', v).group(0)) & 0xFF
        txt = re.sub(r'\d+', '', v)
        arr[off:off+len(txt)] = []
      return ''.join(arr) + '==='

    @staticmethod
    def _decode_chapter_data(data_enc, nonce):
      """Decode chapter data given the base64-encoded data and the nonce"""
      data = base64.b64decode(AcqqChapterExtractor._decrypt_with_nonce(data_enc, nonce))
      data = data.decode('utf-8', errors='ignore')
      data = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', data)
      return data

    # The worst javascript "runtime" you've ever seen
    @staticmethod
    def _eval_js_expr(js_expr):
      """Evaluate a subset of JavaScript expressions needed to calculate the decryption nonce"""
      js_expr = re.sub(r"\((.*?)\).toString\(\)", r"str(\1)", js_expr)
      js_expr = re.sub(r"eval\(\"(.*?)\"\)", r"\1", js_expr)
      js_expr = re.sub(r"Math.pow\((\d+),(\d+)\)", r"(\1**\2)", js_expr)
      js_expr = re.sub(r"(document\.(children|getElements?ByTagName\('html'\))|window\.Array)", "1", js_expr)
      js_expr = re.sub(r"!!!", r"!", js_expr)
      js_expr = re.sub(r"!!(\d+)", r"int(not (not \1))", js_expr)
      js_expr = re.sub(r"\~([0-9.]+)", r"~int(\1)", js_expr)
      js_expr = re.sub(r"!(\d+)", r"int(not \1)", js_expr)
      js_expr = re.sub(r"parseInt", "int", js_expr)
      js_expr = re.sub(r"\.substring\((\d+)\)", r"[\1:]", js_expr)
      js_expr = re.sub(r"\+(['\"])", r"\1", js_expr)
      js_expr = re.sub(r"(if|while|for)", "", js_expr)
      js_expr = re.sub(r"Math.round", "js_round", js_expr)
      js_expr = re.sub(r"'(.)'.charCodeAt\(\)", r"ord('\1')", js_expr)
      js_expr = re.sub(r"(\d+)(<|<=|==|!=|=>|>)(\d+)\?(\d+):(\d+)", r"\4 if \1 \2 \3 else \5", js_expr)
      js_expr = re.sub(r"([^0-9])\.([^0-9])", r"\1\2", js_expr)
      py_expr = js_expr

      # Now we run the translated code in a safe sandbox
      # We'll also add a few functions needed by the translated code
      result = eval(py_expr, {'__builtins__': {
        'str': lambda x: str(int(x)),
        'int': int,
        'ord': ord,
        'js_round': lambda x: int(x+0.5)
      }})
      return result


class AcqqComicExtractor(AcqqBase, Extractor):
    subcategory = "comic"
    categorytransfer = True
    pattern = (BASE_PATTERN + r"$")
    test = (
        ("", {
            "pattern": AcqqChapterExtractor.pattern,
            "count": 32,
        }),
        ("https://comic.naver.com/challenge/list?titleId=765124", {
            "pattern": AcqqChapterExtractor.pattern,
            "count": 25,
        }),
        ("https://comic.naver.com/bestChallenge/list.nhn?titleId=789786", {
            "pattern": AcqqChapterExtractor.pattern,
            "count": ">= 12",
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.path, self.comic_id = match.groups()

    def items(self):
        url = "{}/{}/{}".format(self.root, self.path, self.comic_id)
        data = {"_extractor": AcqqChapterExtractor}

        page = self.request(url).text

        for chapter_id in re.findall(
            r'<a target="_blank" title="(?:[^"]+)"'
            r' href="/ComicView/index/id/(?:[0-9]+)/cid/([0-9]+)"', page):
            chapter_url = "{}/ComicView/index/id/{}/cid/{}".format(self.root, self.comic_id, chapter_id)
            yield Message.Queue, chapter_url, data

