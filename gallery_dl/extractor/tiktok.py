# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.tiktok.com/"""

from .common import Extractor, Message
from .. import text, util, ytdl, exception

BASE_PATTERN = r"(?:https?://)?(?:www\.)?tiktokv?\.com"
USER_PATTERN = BASE_PATTERN + r"/@([\w_.-]+)"


class TiktokExtractor(Extractor):
    """Base class for TikTok extractors"""
    category = "tiktok"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = "{title[b:150]} [{id}{num:?_//}{img_id:?_//}].{extension}"
    archive_fmt = "{id}_{num}_{img_id}"
    root = "https://www.tiktok.com/"
    cookies_domain = ".tiktok.com"

    def urls(self):
        return (self.url,)

    def avatar(self):
        return False

    def items(self):
        videos = self.config("videos", True)
        # We assume that all of the URLs served by urls() come from the same
        # author.
        downloaded_avatar = not self.avatar()

        for tiktok_url in self.urls():
            tiktok_url = self._sanitize_url(tiktok_url)
            data = self._extract_rehydration_data(tiktok_url)
            if "webapp.video-detail" not in data:
                # Only /video/ links result in the video-detail dict we need.
                # Try again using that form of link.
                tiktok_url = self._sanitize_url(
                    data["seo.abtest"]["canonical"])
                data = self._extract_rehydration_data(tiktok_url)
            video_detail = data["webapp.video-detail"]

            if not self._check_status_code(video_detail, tiktok_url):
                continue

            post = video_detail["itemInfo"]["itemStruct"]
            author = post["author"]
            post["user"] = user = author["uniqueId"]
            post["date"] = text.parse_timestamp(post["createTime"])
            original_title = title = post["desc"]
            if not title:
                title = "TikTok photo #{}".format(post["id"])

            if not downloaded_avatar:
                avatar_url = post["author"]["avatarLarger"]
                avatar = text.nameext_from_url(avatar_url, post.copy())
                avatar.update({
                    "type"  : "avatar",
                    "title" : "@" + user,
                    "id"    : author["id"],
                    "img_id": avatar["filename"].partition("~")[0],
                    "num"   : 0,
                })
                yield Message.Directory, avatar
                yield Message.Url, avatar_url, avatar
                downloaded_avatar = True

            yield Message.Directory, post
            if "imagePost" in post:
                img_list = post["imagePost"]["images"]
                for i, img in enumerate(img_list, 1):
                    url = img["imageURL"]["urlList"][0]
                    text.nameext_from_url(url, post)
                    post.update({
                        "type"  : "image",
                        "image" : img,
                        "title" : title,
                        "num"   : i,
                        "img_id": post["filename"].partition("~")[0],
                        "width" : img["imageWidth"],
                        "height": img["imageHeight"],
                    })
                    yield Message.Url, url, post

            elif videos:
                if not original_title:
                    title = "TikTok video #{}".format(post["id"])

            else:
                self.log.info("%s: Skipping post", tiktok_url)

            if videos:
                post.update({
                    "type"      : "video",
                    "image"     : None,
                    "filename"  : "",
                    "extension" : "mp4",
                    "title"     : title,
                    "num"       : 0,
                    "img_id"    : "",
                    "width"     : 0,
                    "height"    : 0,
                })
                yield Message.Url, "ytdl:" + tiktok_url, post

    def _sanitize_url(self, url):
        return text.ensure_http_scheme(url.replace("/photo/", "/video/", 1))

    def _extract_rehydration_data(self, url):
        html = self.request(url).text
        data = text.extr(
            html, '<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" '
            'type="application/json">', '</script>')
        return util.json_loads(data)["__DEFAULT_SCOPE__"]

    def _check_status_code(self, detail, url):
        status = detail.get("statusCode")
        if not status:
            return True

        if status == 10222:
            self.log.error("%s: Login required to access this post", url)
        elif status == 10204:
            self.log.error("%s: Requested post not available", url)
        elif status == 10231:
            self.log.error("%s: Region locked - Try downloading with a"
                           "VPN/proxy connection", url)
        else:
            self.log.error(
                "%s: Received unknown error code %s ('%s')",
                url, status, detail.get("statusMsg") or "")
        return False


class TiktokPostExtractor(TiktokExtractor):
    """Extract a single video or photo TikTok link"""
    subcategory = "post"
    pattern = USER_PATTERN + r"/(?:phot|vide)o/\d+"
    example = "https://www.tiktok.com/@USER/photo/1234567890"


class TiktokVmpostExtractor(TiktokExtractor):
    """Extract a single video or photo TikTok VM link"""
    subcategory = "vmpost"
    pattern = (r"(?:https?://)?(?:"
               r"(?:v[mt]\.)?tiktok\.com|(?:www\.)?tiktok\.com/t"
               r")/(?!@)[^/?#]+")
    example = "https://vm.tiktok.com/1a2B3c4E5"

    def items(self):
        url = text.ensure_http_scheme(self.url)
        headers = {"User-Agent": "facebookexternalhit/1.1"}

        response = self.request(url, headers=headers, method="HEAD",
                                allow_redirects=False, notfound="post")

        url = response.headers.get("Location")
        if not url or len(url) <= 28:
            # https://www.tiktok.com/?_r=1
            raise exception.NotFoundError("post")

        data = {"_extractor": TiktokPostExtractor}
        yield Message.Queue, url.partition("?")[0], data


class TiktokSharepostExtractor(TiktokExtractor):
    """Extract a single video or photo TikTok share link"""
    subcategory = "sharepost"
    pattern = BASE_PATTERN + r"/share/video/\d+"
    example = "https://www.tiktokv.com/share/video/1234567890"


class TiktokUserExtractor(TiktokExtractor):
    """Extract a TikTok user's profile"""
    subcategory = "user"
    pattern = USER_PATTERN + r"/?(?:$|\?|#)"
    example = "https://www.tiktok.com/@USER"

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
                "ignore_no_formats_error": True,
                "cookiefile": self.cookies_file,
                "playlist_items": str(self.config("tiktok-range", "")),
            }
        ) as ydl:
            info = ydl.extract_info(self.url, download=False)
            # This should include video and photo posts in /video/ URL form.
            return [video["webpage_url"] for video in info["entries"]]

    def avatar(self):
        return True
