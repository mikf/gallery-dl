# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.tiktok.com/"""

from .common import Extractor, Message
from .. import exception, text, util
from re import compile, escape, IGNORECASE

BASE_PATTERN = r"(?:https?://)?(?:www\.)?tiktok\.com"
USER_PATTERN = BASE_PATTERN + r"/+@([\w.]{0,23}\w)(?:/\S*)?"
POST_PATTERN = USER_PATTERN + \
    r"/+(?:[pP][hH][oO][tT][oO]|[vV][iI][dD][eE][oO])/+(?:[0-9]+)/*"
VM_POST_PATTERN = r"(?:https?://)?(?:vm\.)?tiktok\.com/+.*/*"


class TiktokExtractor(Extractor):
    """Base class for TikTok extractors"""

    category = "tiktok"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = "{title} [{id}] [{index}].{extension}"
    archive_fmt = "{id}_{img_id}"
    root = "https://www.tiktok.com/"
    cookies_domain = ".tiktok.com"

    def urls(self):
        return [self.url]

    def items(self):
        for tiktok_url in self.urls():
            # If we can recognise that this is a /photo/ link, preemptively
            # replace it with /video/ to prevent a needless second request.
            # See below.
            tiktok_url = compile(
                escape("/photo/"),
                IGNORECASE
            ).sub("/video/", tiktok_url)
            video_detail = util.json_loads(text.extr(
                self.request(tiktok_url).text,
                '<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" '
                'type="application/json">',
                '</script>'
            ))["__DEFAULT_SCOPE__"]
            if "webapp.video-detail" not in video_detail:
                # Only /video/ links result in the video-detail dict we need.
                # Try again using that form of link.
                tiktok_url = video_detail["seo.abtest"]["canonical"] \
                    .replace("/photo/", "/video/")
                video_detail = util.json_loads(text.extr(
                    self.request(tiktok_url).text,
                    '<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" '
                    'type="application/json">',
                    '</script>'
                ))["__DEFAULT_SCOPE__"]
            video_detail = video_detail["webapp.video-detail"]
            has_status = "statusMsg" in video_detail
            if has_status and video_detail["statusMsg"] == "author_secret":
                raise exception.AuthorizationError("Login required to access "
                                                   "this post")
            post_info = video_detail["itemInfo"]["itemStruct"]
            user = post_info["author"]["uniqueId"]
            if "imagePost" in post_info:
                yield Message.Directory, {"user": user}
                img_list = post_info["imagePost"]["images"]
                for i, img in enumerate(img_list):
                    url = img["imageURL"]["urlList"][0]
                    name_and_ext = text.nameext_from_url(url)
                    id = post_info["id"]
                    title = post_info["desc"]
                    if len(title) == 0:
                        title = "TikTok photo #{}".format(id)
                    yield Message.Url, url, {
                        "title"     : text.sanitize_for_filename(title)[:170],
                        "id"        : id,
                        "index"     : i,
                        "img_id"    : name_and_ext["filename"].split("~")[0],
                        "extension" : name_and_ext["extension"],
                        "width"     : img["imageWidth"],
                        "height"    : img["imageHeight"]
                    }
            else:
                # TODO: Not a slide show. Should pass this to yt-dlp.
                pass


class TiktokPostExtractor(TiktokExtractor):
    """Extract a single video or photo TikTok link"""

    subcategory = "post"
    pattern = POST_PATTERN
    example = "https://www.tiktok.com/@chillezy/photo/7240568259186019630"


class TiktokVmpostExtractor(TiktokExtractor):
    """Extract a single video or photo TikTok VM link"""

    subcategory = "vmpost"
    pattern = VM_POST_PATTERN
    example = "https://vm.tiktok.com/ZGdh4WUhr/"


# TODO: Write profile extractor.
