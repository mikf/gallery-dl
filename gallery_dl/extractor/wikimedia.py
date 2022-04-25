# -*- coding: utf-8 -*-

# Copyright 2022-2022 Ailothaen
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Wikimedia and Wikipedia.
(Other Mediawiki instances use the same API,so a similar extractor
could be written)

Various reference:
https://www.mediawiki.org/wiki/API:Query
https://opendata.stackexchange.com/questions/13381/wikimedia-commons-api-image-by-category
"""

from .common import Extractor, Message
import time
import re


class WikimediaArticleExtractor(Extractor):
    category = "wikimedia"
    subcategory = "article"
    filename_fmt = "{filename}.{extension}"
    archive_fmt = "a_{sha1}"
    pattern = r"https?://([a-z]{2,})\.wikipedia\.org/wiki/([^#/\?]+)"
    directory_fmt = ("{category}", "{page}")
    test = (
        ("https://en.wikipedia.org/wiki/Athena"),
        ("https://zh.wikipedia.org/wiki/太阳"),
        ("https://simple.wikipedia.org/wiki/Hydrogen", {
            "count": ">= 2"
        })
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.lang, self.page = match.groups()

    def items(self):
        continuation = None
        gimcontinuation = None

        while True:
            if continuation is None:
                file_list_request = self.request(
                    "https://{lang}.wikipedia.org/w/api.php?action=query&generator=images&format=json&titles={page}&prop=imageinfo&iiprop=timestamp|user|userid|comment|canonicaltitle|url|size|sha1|mime|metadata|commonmetadata|extmetadata|bitdepth".format(  # noqa
                        lang=self.lang, page=self.page
                    )
                )
            else:
                file_list_request = self.request(
                    "https://{lang}.wikipedia.org/w/api.php?action=query&generator=images&format=json&titles={page}&prop=imageinfo&iiprop=timestamp|user|userid|comment|canonicaltitle|url|size|sha1|mime|metadata|commonmetadata|extmetadata|bitdepth&continue={continuation}&gimcontinue={gimcontinuation}".format(  # noqa
                        lang=self.lang,
                        page=self.page,
                        continuation=continuation,
                        gimcontinuation=gimcontinuation,
                    )
                )
            file_list = file_list_request.json()

            for file_index in list(file_list["query"]["pages"]):
                image = file_list["query"]["pages"][file_index]["imageinfo"][0]

                metadata = image
                metadata["filename"] = WikimediaUtils.clean_name(
                    image["canonicaltitle"]
                )[0]
                metadata["extension"] = WikimediaUtils.clean_name(
                    image["canonicaltitle"]
                )[1]

                yield Message.Directory, {"page": self.page, "lang": self.lang}
                yield Message.Url, image["url"], image
            else:
                # We arrived at the end of the response
                # checking if there are more files to retrieve
                try:
                    continuation_info = file_list["continue"]
                except KeyError:
                    # No more continuation info: all files were retrieved
                    break
                else:
                    # Continuation info is present
                    # there are still files to retrieve
                    continuation = continuation_info["continue"]
                    gimcontinuation = continuation_info["gimcontinue"]

            # giving a rest to Wikipedia API
            time.sleep(1)


class WikimediaCategoryExtractor(Extractor):
    category = "wikimedia"
    subcategory = "category"
    filename_fmt = "{filename}.{extension}"
    archive_fmt = "c_{sha1}"
    pattern = r"https?://commons.wikimedia.org/wiki/Category:([^#/\?]+)"
    directory_fmt = ("{category}", "{page}")

    test = (
        ("https://commons.wikimedia.org/wiki/Category:Network_maps_of_the_Paris_Metro"), # noqa
        ("https://commons.wikimedia.org/wiki/Category:Tyto_alba_in_flight_(captive)", { # noqa
            "count": ">= 21"
        })
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.page = match.groups()[0]

    def items(self):
        continuation = None
        gcmcontinuation = None

        while True:
            if continuation is None:
                file_list_request = self.request(
                    "https://commons.wikimedia.org/w/api.php?action=query&generator=categorymembers&gcmtitle=Category:{page}&gcmtype=file&prop=imageinfo&format=json&iiprop=timestamp|user|userid|comment|canonicaltitle|url|size|sha1|mime|metadata|commonmetadata|extmetadata|bitdepth".format(  # noqa
                        page=self.page
                    )
                )
            else:
                file_list_request = self.request(
                    "https://commons.wikimedia.org/w/api.php?action=query&generator=categorymembers&gcmtitle=Category:{page}&gcmtype=file&prop=imageinfo&format=json&iiprop=timestamp|user|userid|comment|canonicaltitle|url|size|sha1|mime|metadata|commonmetadata|extmetadata|bitdepth&continue={continuation}&gcmcontinue={gcmcontinuation}".format(  # noqa
                        page=self.page,
                        continuation=continuation,
                        gcmcontinuation=gcmcontinuation,
                    )
                )
            file_list = file_list_request.json()

            for file_index in list(file_list["query"]["pages"]):
                image = file_list["query"]["pages"][file_index]["imageinfo"][0]

                metadata = image
                metadata["filename"] = WikimediaUtils.clean_name(
                    image["canonicaltitle"]
                )[0]
                metadata["extension"] = WikimediaUtils.clean_name(
                    image["canonicaltitle"]
                )[1]

                yield Message.Directory, {"page": self.page, "lang": "common"}
                yield Message.Url, image["url"], image
            else:
                # We arrived at the end of the response
                # checking if there are more files to retrieve
                try:
                    continuation_info = file_list["continue"]
                except KeyError:
                    # No more continuation info: all files were retrieved
                    break
                else:
                    # Continuation info is present
                    # there are still files to retrieve
                    continuation = continuation_info["continue"]
                    gcmcontinuation = continuation_info["gcmcontinue"]

            # giving a rest to Wikipedia API
            time.sleep(1)


class WikimediaUtils:
    @staticmethod
    def clean_name(name):
        name = re.sub(r"^\w+:", "", name)
        filename = ".".join(name.split(".")[:-1])
        extension = name.split(".")[-1]
        return filename, extension
