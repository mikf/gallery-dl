# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.patreon.com/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import memcache
import collections
import itertools


class PatreonExtractor(Extractor):
    """Base class for patreon extractors"""
    category = "patreon"
    root = "https://www.patreon.com"
    cookies_domain = ".patreon.com"
    directory_fmt = ("{category}", "{creator[full_name]}")
    filename_fmt = "{id}_{title}_{num:>02}.{extension}"
    archive_fmt = "{id}_{num}"
    useragent = "Patreon/72.2.28 (Android; Android 14; Scale/2.10)"
    _warning = True

    def _init(self):
        if not self.cookies_check(("session_id",), subdomains=True):
            if self._warning:
                PatreonExtractor._warning = False
                self.log.warning("no 'session_id' cookie set")
            if self.session.headers["User-Agent"] is self.useragent:
                self.session.headers["User-Agent"] = \
                    "Patreon/7.6.28 (Android; Android 11; Scale/2.10)"

        format_images = self.config("format-images")
        if format_images:
            self._images_fmt = format_images
            self._images_url = self._images_url_fmt

    def items(self):
        generators = self._build_file_generators(self.config("files"))

        for post in self.posts():

            if not post.get("current_user_can_view", True):
                self.log.warning("Not allowed to view post %s", post["id"])
                continue
            yield Message.Directory, post

            post["num"] = 0
            hashes = set()
            for kind, url, name in itertools.chain.from_iterable(
                    g(post) for g in generators):
                fhash = self._filehash(url)
                if fhash not in hashes or not fhash:
                    hashes.add(fhash)
                    post["hash"] = fhash
                    post["type"] = kind
                    post["num"] += 1
                    text.nameext_from_url(name, post)
                    if text.ext_from_url(url) == "m3u8":
                        url = "ytdl:" + url
                        post["_ytdl_manifest"] = "hls"
                        post["extension"] = "mp4"
                    yield Message.Url, url, post
                else:
                    self.log.debug("skipping %s (%s %s)", url, fhash, kind)

    def _postfile(self, post):
        postfile = post.get("post_file")
        if postfile:
            url = postfile["url"]
            name = postfile.get("name")
            if not name:
                if url.startswith("https://stream.mux.com/"):
                    name = url
                else:
                    name = self._filename(url) or url
            return (("postfile", url, name),)
        return ()

    def _images(self, post):
        for image in post.get("images") or ():
            url = self._images_url(image)
            if url:
                name = image.get("file_name") or self._filename(url) or url
                yield "image", url, name

    def _images_url(self, image):
        return image.get("download_url")

    def _images_url_fmt(self, image):
        try:
            return image["image_urls"][self._images_fmt]
        except Exception:
            return image.get("download_url")

    def _image_large(self, post):
        image = post.get("image")
        if image:
            url = image.get("large_url")
            if url:
                name = image.get("file_name") or self._filename(url) or url
                return (("image_large", url, name),)
        return ()

    def _attachments(self, post):
        for attachment in post.get("attachments") or ():
            url = self.request(
                attachment["url"], method="HEAD",
                allow_redirects=False, fatal=False,
            ).headers.get("Location")

            if url:
                yield "attachment", url, attachment["name"]

        for attachment in post.get("attachments_media") or ():
            url = attachment.get("download_url")
            if url:
                yield "attachment", url, attachment["file_name"]

    def _content(self, post):
        content = post.get("content")
        if content:
            for img in text.extract_iter(
                    content, '<img data-media-id="', '>'):
                url = text.extr(img, 'src="', '"')
                if url:
                    yield "content", url, self._filename(url) or url

    def posts(self):
        """Return all relevant post objects"""

    def _pagination(self, url):
        headers = {
            "Content-Type": "application/vnd.api+json",
        }

        while url:
            url = text.ensure_http_scheme(url)
            posts = self.request(url, headers=headers).json()

            if "included" in posts:
                included = self._transform(posts["included"])
                for post in posts["data"]:
                    yield self._process(post, included)

            if "links" not in posts:
                return
            url = posts["links"].get("next")

    def _process(self, post, included):
        """Process and extend a 'post' object"""
        attr = post["attributes"]
        attr["id"] = text.parse_int(post["id"])

        if attr.get("current_user_can_view", True):

            relationships = post["relationships"]
            attr["images"] = self._files(
                post, included, "images")
            attr["attachments"] = self._files(
                post, included, "attachments")
            attr["attachments_media"] = self._files(
                post, included, "attachments_media")
            attr["date"] = text.parse_datetime(
                attr["published_at"], "%Y-%m-%dT%H:%M:%S.%f%z")

            try:
                attr["campaign"] = (included["campaign"][
                                    relationships["campaign"]["data"]["id"]])
            except Exception:
                attr["campaign"] = None

            tags = relationships.get("user_defined_tags")
            attr["tags"] = [
                tag["id"].replace("user_defined;", "")
                for tag in tags["data"]
                if tag["type"] == "post_tag"
            ] if tags else []

            user = relationships["user"]
            attr["creator"] = (
                self._user(user["links"]["related"]) or
                included["user"][user["data"]["id"]])

        return attr

    @staticmethod
    def _transform(included):
        """Transform 'included' into an easier to handle format"""
        result = collections.defaultdict(dict)
        for inc in included:
            result[inc["type"]][inc["id"]] = inc["attributes"]
        return result

    @staticmethod
    def _files(post, included, key):
        """Build a list of files"""
        files = post["relationships"].get(key)
        if files and files.get("data"):
            return [
                included[file["type"]][file["id"]]
                for file in files["data"]
            ]
        return []

    @memcache(keyarg=1)
    def _user(self, url):
        """Fetch user information"""
        response = self.request(url, fatal=False)
        if response.status_code >= 400:
            return None
        user = response.json()["data"]
        attr = user["attributes"]
        attr["id"] = user["id"]
        attr["date"] = text.parse_datetime(
            attr["created"], "%Y-%m-%dT%H:%M:%S.%f%z")
        return attr

    def _filename(self, url):
        """Fetch filename from an URL's Content-Disposition header"""
        response = self.request(url, method="HEAD", fatal=False)
        cd = response.headers.get("Content-Disposition")
        return text.extr(cd, 'filename="', '"')

    @staticmethod
    def _filehash(url):
        """Extract MD5 hash from a download URL"""
        parts = url.partition("?")[0].split("/")
        parts.reverse()

        for part in parts:
            if len(part) == 32:
                return part
        return ""

    @staticmethod
    def _build_url(endpoint, query):
        return (
            "https://www.patreon.com/api/" + endpoint +

            "?include=campaign,access_rules,attachments,attachments_media,"
            "audio,images,media,native_video_insights,poll.choices,"
            "poll.current_user_responses.user,"
            "poll.current_user_responses.choice,"
            "poll.current_user_responses.poll,"
            "user,user_defined_tags,ti_checks"

            "&fields[campaign]=currency,show_audio_post_download_links,"
            "avatar_photo_url,avatar_photo_image_urls,earnings_visibility,"
            "is_nsfw,is_monthly,name,url"

            "&fields[post]=change_visibility_at,comment_count,commenter_count,"
            "content,current_user_can_comment,current_user_can_delete,"
            "current_user_can_view,current_user_has_liked,embed,image,"
            "insights_last_updated_at,is_paid,like_count,meta_image_url,"
            "min_cents_pledged_to_view,post_file,post_metadata,published_at,"
            "patreon_url,post_type,pledge_url,preview_asset_type,thumbnail,"
            "thumbnail_url,teaser_text,title,upgrade_url,url,"
            "was_posted_by_campaign_owner,has_ti_violation,moderation_status,"
            "post_level_suspension_removal_date,pls_one_liners_by_category,"
            "video_preview,view_count"

            "&fields[post_tag]=tag_type,value"
            "&fields[user]=image_url,full_name,url"
            "&fields[access_rule]=access_rule_type,amount_cents"
            "&fields[media]=id,image_urls,download_url,metadata,file_name"
            "&fields[native_video_insights]=average_view_duration,"
            "average_view_pct,has_preview,id,last_updated_at,num_views,"
            "preview_views,video_duration" + query +

            "&json-api-version=1.0"
        )

    def _build_file_generators(self, filetypes):
        if filetypes is None:
            return (self._images, self._image_large,
                    self._attachments, self._postfile, self._content)
        genmap = {
            "images"     : self._images,
            "image_large": self._image_large,
            "attachments": self._attachments,
            "postfile"   : self._postfile,
            "content"    : self._content,
        }
        if isinstance(filetypes, str):
            filetypes = filetypes.split(",")
        return [genmap[ft] for ft in filetypes]

    def _extract_bootstrap(self, page):
        try:
            data = self._extract_nextdata(page)
            env = data["props"]["pageProps"]["bootstrapEnvelope"]
            return env.get("pageBootstrap") or env["bootstrap"]
        except Exception as exc:
            self.log.debug("%s: %s", exc.__class__.__name__, exc)

        bootstrap = text.extr(
            page, 'window.patreon = {"bootstrap":', '},"apiServer"')
        if bootstrap:
            return util.json_loads(bootstrap + "}")

        bootstrap = text.extr(
            page,
            'window.patreon = wrapInProxy({"bootstrap":',
            '},"apiServer"')
        if bootstrap:
            return util.json_loads(bootstrap + "}")

        bootstrap = text.extr(page, "window.patreon.bootstrap,", "});")
        if bootstrap:
            return util.json_loads(bootstrap + "}")

        data = text.extr(page, "window.patreon = {", "};\n")
        if data:
            try:
                return util.json_loads("{" + data + "}")["bootstrap"]
            except Exception:
                pass

        raise exception.StopExtraction("Unable to extract bootstrap data")


class PatreonCreatorExtractor(PatreonExtractor):
    """Extractor for a creator's works"""
    subcategory = "creator"
    pattern = (r"(?:https?://)?(?:www\.)?patreon\.com"
               r"/(?!(?:home|create|login|signup|search|posts|messages)"
               r"(?:$|[/?#]))"
               r"(?:profile/creators|(?:c/)?([^/?#]+)(?:/posts)?)"
               r"/?(?:\?([^#]+))?")
    example = "https://www.patreon.com/c/USER"

    def posts(self):
        creator, query = self.groups

        query = text.parse_query(query)
        campaign_id = self._get_campaign_id(creator, query)
        filters = self._get_filters(query)

        self.log.debug("campaign_id: %s", campaign_id)

        url = self._build_url("posts", (
            "&filter[campaign_id]=" + campaign_id +
            "&filter[contains_exclusive_posts]=true"
            "&filter[is_draft]=false" + filters +
            "&sort=" + query.get("sort", "-published_at")
        ))
        return self._pagination(url)

    def _get_campaign_id(self, creator, query):
        if creator and creator.startswith("id:"):
            return creator[3:]

        campaign_id = query.get("c") or query.get("campaign_id")
        if campaign_id:
            return campaign_id

        user_id = query.get("u")
        if user_id:
            url = "{}/user?u={}".format(self.root, user_id)
        else:
            url = "{}/{}".format(self.root, creator)
        page = self.request(url, notfound="creator").text

        try:
            data = None
            data = self._extract_bootstrap(page)
            return data["campaign"]["data"]["id"]
        except Exception as exc:
            if data:
                self.log.debug(data)
            raise exception.StopExtraction(
                "Unable to extract campaign ID (%s: %s)",
                exc.__class__.__name__, exc)

    def _get_filters(self, query):
        return "".join(
            "&filter[{}={}".format(key[8:], text.escape(value))
            for key, value in query.items()
            if key.startswith("filters[")
        )


class PatreonUserExtractor(PatreonExtractor):
    """Extractor for media from creators supported by you"""
    subcategory = "user"
    pattern = r"(?:https?://)?(?:www\.)?patreon\.com/home$"
    example = "https://www.patreon.com/home"

    def posts(self):
        url = self._build_url("stream", (
            "&page[cursor]=null"
            "&filter[is_following]=true"
            "&json-api-use-default-includes=false"
        ))
        return self._pagination(url)


class PatreonPostExtractor(PatreonExtractor):
    """Extractor for media from a single post"""
    subcategory = "post"
    pattern = r"(?:https?://)?(?:www\.)?patreon\.com/posts/([^/?#]+)"
    example = "https://www.patreon.com/posts/TITLE-12345"

    def posts(self):
        url = "{}/posts/{}".format(self.root, self.groups[0])
        page = self.request(url, notfound="post").text
        bootstrap = self._extract_bootstrap(page)

        try:
            post = bootstrap["post"]
        except KeyError:
            self.log.debug(bootstrap)
            if bootstrap.get("campaignDisciplinaryStatus") == "suspended":
                self.log.warning("Account suspended")
            return ()

        included = self._transform(post["included"])
        return (self._process(post["data"], included),)
