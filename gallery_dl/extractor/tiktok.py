# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.tiktok.com/"""

from .common import Extractor, Message
from .. import text, util, ytdl, exception

BASE_PATTERN = r"(?:https?://)?(?:www\.)?tiktokv?\.com"


class TiktokExtractor(Extractor):
    """Base class for TikTok extractors"""
    category = "tiktok"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = (
        "{id}{num:?_//>02} {title[b:150]}{img_id:? [/]/}.{extension}")
    archive_fmt = "{id}_{num}_{img_id}"
    root = "https://www.tiktok.com"
    cookies_domain = ".tiktok.com"

    def _init(self):
        self.audio = self.config("audio", True)
        self.video = self.config("videos", True)
        if not self.config("avatar", True):
            self.avatar = util.false

    def items(self):
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

            if not downloaded_avatar:
                avatar_url = author["avatarLarger"]
                avatar = self._generate_avatar(
                    avatar_url, post, user, author["id"])
                yield Message.Directory, avatar
                yield Message.Url, avatar_url, avatar
                downloaded_avatar = True

            yield Message.Directory, post
            ytdl_media = False

            if "imagePost" in post:
                if not original_title:
                    title = "TikTok photo #{}".format(post["id"])
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

                if self.audio and "music" in post:
                    ytdl_media = "audio"

            elif self.video and "video" in post:
                ytdl_media = "video"

            else:
                self.log.info("%s: Skipping post", tiktok_url)

            if ytdl_media:
                if not original_title:
                    title = "TikTok {} #{}".format(ytdl_media, post["id"])
                post.update({
                    "type"      : ytdl_media,
                    "image"     : None,
                    "filename"  : "",
                    "extension" : "mp3" if ytdl_media == "audio" else "mp4",
                    "title"     : title,
                    "num"       : 0,
                    "img_id"    : "",
                    "width"     : 0,
                    "height"    : 0,
                })
                yield Message.Url, "ytdl:" + tiktok_url, post

        # If we couldn't download the avatar because the given user has no
        # posts, we'll need to make a separate request for the user's page
        # and download the avatar that way.
        if not downloaded_avatar:
            user_name = self.avatar()
            profile_url = "https://www.tiktok.com/@{}".format(user_name)
            data = self._extract_rehydration_data(profile_url)
            data = data["webapp.user-detail"]["userInfo"]["user"]
            data["user"] = user_name
            avatar_url = data["avatarLarger"]
            avatar = self._generate_avatar(
                avatar_url, data, user_name, data["id"])
            yield Message.Directory, avatar
            yield Message.Url, avatar_url, avatar

    def avatar(self):
        return False

    def _generate_avatar(self, avatar_url, data, user_name, user_id):
        avatar = text.nameext_from_url(avatar_url, data.copy())
        avatar.update({
            "type"  : "avatar",
            "title" : "@" + user_name,
            "id"    : user_id,
            "img_id": avatar["filename"].partition("~")[0],
            "num"   : 0,
        })
        return avatar

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
    pattern = BASE_PATTERN + r"/(?:@([\w_.-]*)|share)/(?:phot|vide)o/(\d+)"
    example = "https://www.tiktok.com/@USER/photo/1234567890"

    def urls(self):
        user, post_id = self.groups
        url = "{}/@{}/video/{}".format(self.root, user or "", post_id)
        return (url,)


class TiktokVmpostExtractor(TiktokExtractor):
    """Extract a single video or photo TikTok VM link"""
    subcategory = "vmpost"
    pattern = (r"(?:https?://)?(?:"
               r"(?:v[mt]\.)?tiktok\.com|(?:www\.)?tiktok\.com/t"
               r")/(?!@)([^/?#]+)")
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


class TiktokUserExtractor(TiktokExtractor):
    """Extract a TikTok user's profile"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/@([\w_.-]+)/?(?:$|\?|#)"
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

        ytdl_range = self.config("tiktok-range")
        if ytdl_range is None or not ytdl_range and ytdl_range != 0:
            ytdl_range = ""

        extr_opts = {
            "extract_flat"           : True,
            "ignore_no_formats_error": True,
        }
        user_opts = {
            "retries"                : self._retries,
            "socket_timeout"         : self._timeout,
            "nocheckcertificate"     : not self._verify,
            "playlist_items"         : str(ytdl_range),
        }
        if self._proxies:
            user_opts["proxy"] = self._proxies.get("http")

        ytdl_instance = ytdl.construct_YoutubeDL(
            module, self, user_opts, extr_opts)

        # transfer cookies to ytdl
        if self.cookies:
            set_cookie = ytdl_instance.cookiejar.set_cookie
            for cookie in self.cookies:
                set_cookie(cookie)

        with ytdl_instance as ydl:
            info_dict = ydl._YoutubeDL__extract_info(
                "{}/@{}".format(self.root, self.groups[0]),
                ydl.get_info_extractor("TikTokUser"),
                False, {}, True)
            # This should include video and photo posts in /video/ URL form.
            return [video["url"] for video in info_dict["entries"]]

    def avatar(self):
        return self.groups[0]
