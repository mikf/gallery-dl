# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://weverse.io/"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache
import binascii
import hashlib
import hmac
import time
import urllib.parse
import uuid
from collections import OrderedDict
from http import HTTPStatus

BASE_PATTERN = r"^(?:https?://)?(?:m\.)?weverse\.io/([^/?#]+)"
MEMBER_ID_PATTERN = r"/([a-f0-9]+)"
POST_ID_PATTERN = r"/(\d-\d+)"


class WeverseExtractor(Extractor):
    """Base class for weverse extractors"""

    category = "weverse"
    filename_fmt = "{category}_{id}.{extension}"
    archive_fmt = "{category}_{post_id}_{id}"
    cookies_domain = ".weverse.io"
    cookies_names = ("we2_access_token",)
    root = "https://weverse.io"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.post_url = match.group(0)
        self.community_keyword = match.group(1)

    def _init(self):
        self.embeds = self.config("embeds", True)
        self.videos = self.config("videos", True)

    def items(self):
        self.login()
        self.api = WeverseAPI(self)

        post = self.post()
        data = self.metadata(post)

        files = []
        if post["attachment"]:
            self._extract_post(post, files)
        elif post["extension"]:
            if isinstance(self, WeverseMomentExtractor):
                self._extract_moment(post, files)
            else:
                self._extract_media(post["extension"], files)
        data["count"] = len(files)

        yield Message.Directory, data
        for file in files:
            file.update(data)
            url = file.pop("url")
            yield Message.Url, url, file

    def _extract_image(self, image):
        url = image["url"]
        return {
            "id": image["photoId"],
            "url": url,
            "width": image["width"],
            "height": image["height"],
            "extension": text.ext_from_url(url),
        }

    def _extract_video(self, video):
        video_id = video["videoId"]
        if isinstance(self, WeverseMediaExtractor):
            master_id = (
                video.get("uploadInfo", {}).get(
                    "videoId") or video["infraVideoId"]
            )
            best_video = self.get_best_video(
                self.api.get_media_video_list(video_id, master_id),
            )
        else:
            best_video = self.get_best_video(
                self.api.get_post_video_list(video_id))
        url = best_video["source"]
        return {
            "id": video_id,
            "url": url,
            "width": best_video["encodingOption"]["width"],
            "height": best_video["encodingOption"]["height"],
            "extension": text.ext_from_url(url),
        }

    def _extract_embed(self, embed):
        return {
            "id": embed["youtubeVideoId"],
            "extension": None,
            "url": "ytdl:" + embed["videoPath"],
        }

    def _extract_post(self, post, files):
        attachments = {}
        attachments.update(post["attachment"].get("photo", {}))
        attachments.update(post["attachment"].get("video", {}))

        # the order of attachments in the api response can differ to the order
        # of attachments on the site
        attachment_order = list(text.extract_iter(post["body"], 'id="', '"'))
        for index, attachment_id in enumerate(attachment_order, 1):
            file = {
                "num": index,
            }
            attachment = attachments[attachment_id]
            if "photoId" in attachment:
                file.update(self._extract_image(attachment))
            else:
                file.update(self._extract_video(attachment))
            files.append(file)

    def _extract_moment(self, post, files):
        moment = next(
            post["extension"][key]
            for key in ("moment", "momentW1")
            if key in post["extension"]
        )
        if not moment:
            return

        file = {
            "num": 1,
        }
        if "photo" in moment:
            file.update(self._extract_image(moment["photo"]))
        else:
            if not self.videos:
                return
            file.update(self._extract_video(moment["video"]))

        files.append(file)

    def _extract_media(self, extension, files):
        if "image" in extension:
            for index, photo in enumerate(extension["image"]["photos"], 1):
                file = self._extract_image(photo)
                file["num"] = index
                files.append(file)
        elif "video" in extension:
            if not self.videos:
                return
            file = self._extract_video(extension["video"])
            files.append(file)
        else:
            if not self.embeds or not self.videos:
                return
            file = self._extract_embed(extension["youtube"])
            file["num"] = 1
            files.append(file)

    def get_best_video(self, videos):
        return max(
            videos,
            key=lambda video: video["encodingOption"]["width"] *
            video["encodingOption"]["height"],
        )

    def metadata(self, post):
        published_at = text.parse_timestamp(post["publishedAt"] / 1000)
        data = {
            "date": published_at,
            "post_url": post.get("shareUrl", self.post_url),
            "post_id": post["postId"],
            "post_type": post["postType"],
            "section_type": post["sectionType"],
        }

        if "hideFromArtist" in post:
            data["hide_from_artist"] = post["hideFromArtist"]

        if "membershipOnly" in post:
            data["membership_only"] = post["membershipOnly"]

        if post.get("tags", []):
            data["tags"] = post["tags"]

        if "author" in post:
            author = {
                "id": post["author"]["memberId"],
                "name": post["author"]["profileName"],
                "profile_type": post["author"]["profileType"],
            }
            if "artistOfficialProfile" in post["author"]:
                artist_profile = post["author"]["artistOfficialProfile"]
                author["name"] = artist_profile["officialName"]
            data["author"] = author

        if "community" in post:
            community = {
                "id": post["community"]["communityId"],
                "name": post["community"]["communityName"],
                "artist_code": post["community"]["artistCode"],
            }
            data["community"] = community

        extension = post["extension"]
        media_info = extension.get("mediaInfo", {})
        if media_info:
            categories = [
                {
                    "id": category["id"],
                    "type": category["type"],
                    "title": category["title"],
                }
                for category in media_info["categories"]
            ]
            data.update(
                {
                    "title": media_info["title"],
                    "media_type": media_info["mediaType"],
                    "categories": categories,
                },
            )

        moment = next(
            (extension[key]
             for key in ("moment", "momentW1") if key in extension),
            None,
        )
        if moment:
            expire_at = text.parse_timestamp(moment["expireAt"] / 1000)
            data["expire_at"] = expire_at

        return data

    def post(self):
        return {}

    def login(self):
        if self.cookies_check(self.cookies_names):
            return

        username, password = self._get_auth_info()
        if username:
            self.cookies_update(_login_impl(self, username, password))


class WeversePostExtractor(WeverseExtractor):
    """Extractor for a weverse community post"""

    subcategory = "post"
    directory_fmt = (
        "{category}", "{community[name]}", "{author[id]}", "{post_id}")
    pattern = BASE_PATTERN + r"/(?:artist|fanpost)" + POST_ID_PATTERN
    example = "https://weverse.io/abcdef/artist/1-123456789"

    def __init__(self, match):
        WeverseExtractor.__init__(self, match)
        self.post_id = match.group(2)

    def post(self):
        return self.api.get_post(self.post_id)


class WeverseMemberExtractor(WeverseExtractor):
    """Extractor for all posts from a weverse community member"""

    subcategory = "member"
    pattern = BASE_PATTERN + "/profile" + MEMBER_ID_PATTERN + r"$"
    example = "https://weverse.io/abcdef/profile/a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5"  # noqa E501

    def __init__(self, match):
        WeverseExtractor.__init__(self, match)
        self.member_id = match.group(2)

    def items(self):
        self.login()
        self.api = WeverseAPI(self)

        data = {"_extractor": WeversePostExtractor}
        posts = self.api.get_member_posts(self.member_id)
        for post in posts:
            yield Message.Queue, post["shareUrl"], data


class WeverseFeedExtractor(WeverseExtractor):
    """Extractor for a weverse community feed"""

    subcategory = "feed"
    pattern = BASE_PATTERN + r"/(feed|artist)$"
    example = "https://weverse.io/abcdef/feed"

    def __init__(self, match):
        WeverseExtractor.__init__(self, match)
        self.feed_name = match.group(2)

    def items(self):
        self.login()
        self.api = WeverseAPI(self)

        data = {"_extractor": WeversePostExtractor}
        posts = self.api.get_feed_posts(self.community_keyword, self.feed_name)
        for post in posts:
            yield Message.Queue, post["shareUrl"], data


class WeverseMomentExtractor(WeverseExtractor):
    """Extractor for a weverse community artist moment"""

    subcategory = "moment"
    pattern = (BASE_PATTERN + "/moment" +
               MEMBER_ID_PATTERN + "/post" +
               POST_ID_PATTERN)
    example = "https://weverse.io/abcdef/moment/a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5/post/1-123456789"  # noqa E501

    def __init__(self, match):
        WeverseExtractor.__init__(self, match)
        self.post_id = match.group(3)

    def post(self):
        return self.api.get_post(self.post_id)


class WeverseMomentsExtractor(WeverseExtractor):
    """Extractor for all moments from a weverse community artist"""

    subcategory = "moments"
    pattern = BASE_PATTERN + "/moment" + MEMBER_ID_PATTERN + r"$"
    example = "https://weverse.io/abcdef/moment/a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5"  # noqa E501

    def __init__(self, match):
        WeverseExtractor.__init__(self, match)
        self.member_id = match.group(2)

    def items(self):
        self.login()
        self.api = WeverseAPI(self)

        data = {"_extractor": WeverseMomentExtractor}
        moments = self.api.get_member_moments(self.member_id)
        for moment in moments:
            yield Message.Queue, moment["shareUrl"], data


class WeverseMediaExtractor(WeverseExtractor):
    """Extractor for a weverse community media post"""

    subcategory = "media"
    directory_fmt = ("{category}", "{community[name]}", "media", "{post_id}")
    pattern = BASE_PATTERN + "/media" + POST_ID_PATTERN
    example = "https://weverse.io/abcdef/media/1-123456789"

    def __init__(self, match):
        WeverseExtractor.__init__(self, match)
        self.post_id = match.group(2)

    def post(self):
        return self.api.get_post(self.post_id)


class WeverseMediaTabExtractor(WeverseExtractor):
    """Extractor for the media tab of a weverse community"""

    subcategory = "media-tab"
    pattern = BASE_PATTERN + r"/media(?:/(all|membership|new))?$"
    example = "https://weverse.io/abcdef/media"

    def __init__(self, match):
        WeverseExtractor.__init__(self, match)
        self.tab_name = match.group(2) or "all"

    def items(self):
        self.login()
        self.api = WeverseAPI(self)

        data = {"_extractor": WeverseMediaExtractor}
        if self.tab_name == "new":
            get_media = self.api.get_latest_community_media
        elif self.tab_name == "membership":
            get_media = self.api.get_membership_community_media
        else:
            get_media = self.api.get_all_community_media
        medias = get_media(self.community_keyword)
        for media in medias:
            yield Message.Queue, media["shareUrl"], data


class WeverseMediaCategoryExtractor(WeverseExtractor):
    """Extractor for media by category of a weverse community"""

    subcategory = "media-category"
    pattern = BASE_PATTERN + r"/media/category/(\d+)"
    example = "https://weverse.io/abcdef/media/category/1234"

    def __init__(self, match):
        WeverseExtractor.__init__(self, match)
        self.media_category = match.group(2)

    def items(self):
        self.login()
        self.api = WeverseAPI(self)

        data = {"_extractor": WeverseMediaExtractor}
        medias = self.api.get_media_by_category_id(self.media_category)
        for media in medias:
            yield Message.Queue, media["shareUrl"], data


class WeverseAPI:
    """Interface for the Weverse API"""

    BASE_API_URL = "https://global.apis.naver.com"
    WMD_API_URL = BASE_API_URL + "/weverse/wevweb"
    VOD_API_URL = BASE_API_URL + "/rmcnmv/rmcnmv"

    APP_ID = "be4d79eb8fc7bd008ee82c8ec4ff6fd4"
    SECRET = "1b9cb6378d959b45714bec49971ade22e6e24e42"

    def __init__(self, extractor):
        self.extractor = extractor

        cookies = extractor.cookies
        token_cookie_name = extractor.cookies_names[0]
        cookies_domain = extractor.cookies_domain
        self.access_token = cookies.get(
            token_cookie_name, domain=cookies_domain)
        self.headers = (
            {"Authorization": "Bearer " + self.access_token}
            if self.access_token
            else None
        )

    def _endpoint_with_params(self, endpoint, params):
        params_delimiter = "?"
        if "?" in endpoint:
            params_delimiter = "&"
        return (endpoint + params_delimiter +
                urllib.parse.urlencode(query=params))

    def _message_digest(self, endpoint, params, timestamp):
        key = self.SECRET.encode()
        url = self._endpoint_with_params(endpoint, params)
        message = "{}{}".format(url[:255], timestamp).encode()
        hash_digest = hmac.new(key, message, hashlib.sha1).digest()
        return binascii.b2a_base64(hash_digest).rstrip().decode()

    def _apply_no_auth(self, endpoint, params):
        if not endpoint.endswith("/preview"):
            endpoint += "/preview"
        params.update({"fieldSet": "postForPreview"})
        return endpoint, params

    def _is_text_only(self, post):
        for key in ("attachment", "extension"):
            if post.get(key, {}):
                return False
        if "summary" in post:
            s = post["summary"]
            if s.get("videoCount", 0) + s.get("photoCount", 0) > 0:
                return False
        return True

    def get_in_key(self, video_id):
        endpoint = "/video/v1.1/vod/{}/inKey".format(video_id)
        return self._call_wmd(endpoint, method="POST")["inKey"]

    def get_community_id(self, community_keyword):
        endpoint = "/community/v1.0/communityIdUrlPathByUrlPathArtistCode"
        params = {"keyword": community_keyword}
        return self._call_wmd(endpoint, params)["communityId"]

    def get_post(self, post_id):
        endpoint = "/post/v1.0/post-{}".format(post_id)
        params = {"fieldSet": "postV1"}
        if not self.access_token:
            endpoint, params = self._apply_no_auth(endpoint, params)
        return self._call_wmd(endpoint, params)

    def get_media_video_list(self, video_id, master_id):
        in_key = self.get_in_key(video_id)
        url = "{}/vod/play/v2.0/{}".format(self.VOD_API_URL, master_id)
        params = {"key": in_key}
        res = self._call(url, params=params)
        return res["videos"]["list"]

    def get_post_video_list(self, video_id):
        endpoint = "/cvideo/v1.0/cvideo-{}/playInfo".format(video_id)
        params = {"videoId": video_id}
        res = self._call_wmd(endpoint, params=params)
        return res["playInfo"]["videos"]["list"]

    def get_member_posts(self, member_id):
        endpoint = "/post/v1.0/member-{}/posts".format(member_id)
        params = {
            "fieldSet": "postsV1",
            "filterType": "DEFAULT",
            "limit": 20,
            "sortType": "LATEST",
        }
        return self._pagination(endpoint, params)

    def get_feed_posts(self, community_keyword, feed_name):
        community_id = self.get_community_id(community_keyword)
        endpoint = "/post/v1.0/community-{}/{}TabPosts".format(
            community_id, feed_name)
        params = {
            "fieldSet": "postsV1",
            "limit": 20,
            "pagingType": "CURSOR",
        }
        return self._pagination(endpoint, params)

    def get_latest_community_media(self, community_keyword):
        community_id = self.get_community_id(community_keyword)
        endpoint = "/media/v1.0/community-{}/more".format(community_id)
        params = {
            "fieldSet": "postsV1",
            "filterType": "RECENT",
        }
        return self._pagination(endpoint, params)

    def get_membership_community_media(self, community_keyword):
        community_id = self.get_community_id(community_keyword)
        endpoint = "/media/v1.0/community-{}/more".format(community_id)
        params = {
            "fieldSet": "postsV1",
            "filterType": "MEMBERSHIP",
        }
        return self._pagination(endpoint, params)

    def get_all_community_media(self, community_keyword):
        community_id = self.get_community_id(community_keyword)
        endpoint = "/media/v1.0/community-{}/searchAllMedia".format(
            community_id)
        params = {
            "fieldSet": "postsV1",
            "sortOrder": "DESC",
        }
        return self._pagination(endpoint, params)

    def get_media_by_category_id(self, category_id):
        endpoint = "/media/v1.0/category-{}/mediaPosts".format(category_id)
        params = {
            "fieldSet": "postsV1",
            "sortOrder": "DESC",
        }
        return self._pagination(endpoint, params)

    def get_member_moments(self, member_id):
        endpoint = "/post/v1.0/member-{}/posts".format(member_id)
        params = {
            "fieldSet": "postsV1",
            "filterType": "MOMENT",
            "limit": 1,
        }
        return self._pagination(endpoint, params)

    def _call(self, url, **kwargs):
        while True:
            try:
                return self.extractor.request(url, **kwargs).json()
            except exception.HttpError as exc:
                if exc.response.status_code == HTTPStatus.UNAUTHORIZED:
                    raise exception.AuthenticationError() from None
                if exc.response.status_code == HTTPStatus.FORBIDDEN:
                    raise exception.AuthorizationError(
                        "Post requires membership",
                    ) from None
                if exc.response.status_code == HTTPStatus.NOT_FOUND:
                    raise exception.NotFoundError(
                        self.extractor.subcategory) from None
                self.extractor.log.debug(exc)
                return None

    def _call_wmd(self, endpoint, params=None, **kwargs):
        if params is None:
            params = {}
        params.update(
            {
                "appId": self.APP_ID,
                "language": "en",
                "os": "WEB",
                "platform": "WEB",
                "wpf": "pc",
            },
        )
        # the param order is important for the message digest
        params = OrderedDict(sorted(params.items()))
        timestamp = int(time.time() * 1000)
        message_digest = self._message_digest(endpoint, params, timestamp)
        params.update(
            {
                "wmsgpad": timestamp,
                "wmd": message_digest,
            },
        )
        return self._call(
            self.WMD_API_URL + endpoint,
            params=params,
            headers=self.headers,
            **kwargs,
        )

    def _pagination(self, endpoint, params=None):
        if not self.access_token:
            raise exception.AuthenticationError()
        if params is None:
            params = {}
        while True:
            res = self._call_wmd(endpoint, params)
            for post in res["data"]:
                if not self._is_text_only(post):
                    yield post
            np = res.get("paging", {}).get("nextParams", {})
            if "after" not in np:
                return
            params["after"] = np["after"]


@cache(maxage=365 * 24 * 3600, keyarg=1)
def _login_impl(extr, username, password):
    url = "https://accountapi.weverse.io/web/api/v2/auth/token/by-credentials"
    data = {"email": username, "password": password}
    headers = {
        "x-acc-app-secret": "5419526f1c624b38b10787e5c10b2a7a",
        "x-acc-app-version": "3.3.3",
        "x-acc-language": "en",
        "x-acc-service-id": "weverse",
        "x-acc-trace-id": str(uuid.uuid4()),
    }
    extr.log.info("Logging in as %s", username)
    res = extr.request(url, method="POST", json=data, headers=headers).json()
    if "accessToken" not in res:
        extr.log.warning(
            "Unable to log in as %s, proceeding without auth", username)
    return {cookie.name: cookie.value for cookie in extr.cookies}
