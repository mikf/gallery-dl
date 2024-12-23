# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.tiktok.com/"""

from .common import Extractor, Message
from .. import exception, text, util, ytdl
from re import compile, escape, IGNORECASE

BASE_PATTERN = r"(?:https?://)?(?:www\.)?tiktok\.com"
USER_PATTERN = BASE_PATTERN + r"/+@([\w.]{0,23}\w)?"
POST_PATTERN = USER_PATTERN + \
    r"/+(?:[pP][hH][oO][tT][oO]|[vV][iI][dD][eE][oO])/+(?:[0-9]+)/*"
VM_POST_PATTERN = r"(?:https?://)?(?:vm\.)?tiktok\.com/+.*/*"


class TiktokExtractor(Extractor):
    """Base class for TikTok extractors"""

    category = "tiktok"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = "{title} [{id}{index:?_//}{img_id:?_//}].{extension}"
    archive_fmt = "{id}_{index}_{img_id}"
    root = "https://www.tiktok.com/"
    cookies_domain = ".tiktok.com"

    def urls(self):
        return [self.url]

    def items(self):
        videos = self.config("videos", True)
        for tiktok_url in self.urls():
            # If we can recognise that this is a /photo/ link, preemptively
            # replace it with /video/ to prevent a needless second request.
            # See below.
            tiktok_url_to_use = compile(
                escape("/photo/"),
                IGNORECASE
            ).sub("/video/", tiktok_url)
            video_detail = util.json_loads(text.extr(
                self.request(tiktok_url_to_use).text,
                '<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" '
                'type="application/json">',
                '</script>'
            ))["__DEFAULT_SCOPE__"]
            if "webapp.video-detail" not in video_detail:
                # Only /video/ links result in the video-detail dict we need.
                # Try again using that form of link.
                tiktok_url_to_use = video_detail["seo.abtest"]["canonical"] \
                    .replace("/photo/", "/video/")
                video_detail = util.json_loads(text.extr(
                    self.request(tiktok_url_to_use).text,
                    '<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" '
                    'type="application/json">',
                    '</script>'
                ))["__DEFAULT_SCOPE__"]
            video_detail = video_detail["webapp.video-detail"]
            if "statusCode" in video_detail:
                if video_detail["statusCode"] == 10222:
                    raise exception.AuthorizationError(
                        tiktok_url + ": Login required to access this post"
                    )
                elif video_detail["statusCode"] == 10204:
                    raise exception.NotFoundError(tiktok_url)
                elif video_detail["statusCode"] == 10231:
                    raise exception.ExtractionError(
                        tiktok_url + " is region locked, try downloading with "
                        "a VPN/proxy connection"
                    )
                elif video_detail["statusCode"] != 0:
                    raise exception.ExtractionError(
                        tiktok_url + ": Received unknown error code " +
                        str(video_detail['statusCode']) + " with message " +
                        (video_detail['statusMsg'] if
                            "statusMsg" in video_detail else "")
                    )
            post_info = video_detail["itemInfo"]["itemStruct"]
            id = post_info["id"]
            original_title = title = post_info["desc"]
            if len(original_title) == 0:
                title = "TikTok photo #{}".format(id)
            title = title[:150]
            user = post_info["author"]["uniqueId"]
            if "imagePost" in post_info:
                yield Message.Directory, {"user": user}
                img_list = post_info["imagePost"]["images"]
                for i, img in enumerate(img_list):
                    url = img["imageURL"]["urlList"][0]
                    name_and_ext = text.nameext_from_url(url)
                    yield Message.Url, url, {
                        "title"     : title,
                        "id"        : id,
                        "index"     : i + 1,
                        "img_id"    : name_and_ext["filename"].split("~")[0],
                        "extension" : name_and_ext["extension"],
                        "width"     : img["imageWidth"],
                        "height"    : img["imageHeight"]
                    }
            elif videos:
                # It's probably obvious but I thought it was worth noting
                # because I got stuck on this for a while: make sure to emit
                # a Directory message before attempting to download anything
                # with yt-dlp! Otherwise you'll run into NoneType, set_filename
                # errors since the download job doesn't get initialized.
                yield Message.Directory, {"user": user}
                if len(original_title) == 0:
                    title = "TikTok video #{}".format(id)
                    title = title[:150]
            else:
                self.log.info("Skipping video post %s", tiktok_url)
            if videos:
                yield Message.Url, "ytdl:" + tiktok_url_to_use, {
                    "filename"  : "",
                    "extension" : "",
                    "title"     : title,
                    "id"        : id,
                    "index"     : "",
                    "img_id"    : ""
                }


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


class TiktokUserExtractor(TiktokExtractor):
    """Extract a TikTok user's profile"""

    subcategory = "user"
    pattern = USER_PATTERN + r"/*$"
    example = "https://www.tiktok.com/@chillezy"

    def urls(self):
        """Attempt to use yt-dlp/youtube-dl to extract links from a
        user's page"""

        try:
            module = ytdl.import_module(self.config("module"))
        except (ImportError, SyntaxError) as exc:
            self.log.error("Cannot import module '%s'",
                           getattr(exc, "name", ""))
            self.log.debug("", exc_info=exc)
            raise exception.ExtractionError("yt-dlp or youtube-dl is required "
                                            "for this feature!")
        with ytdl.construct_YoutubeDL(
            module=module,
            obj=self,
            user_opts={
                "cookiefile": self.cookies_file,
                "playlist_items": str(self.config("tiktok-range", ""))
            }
        ) as ydl:
            info = ydl.extract_info(self.url, download=False)
            # This should include video and photo posts in /video/ URL form.
            return [video["webpage_url"] for video in info["entries"]]
