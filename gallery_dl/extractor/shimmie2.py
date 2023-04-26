# -*- coding: utf-8 -*-

# Copyright 2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Shimmie2 instances"""

from .common import BaseExtractor, Message
from .. import text


class Shimmie2Extractor(BaseExtractor):
    """Base class for shimmie2 extractors"""
    basecategory = "shimmie2"
    filename_fmt = "{category}_{id}{md5:?_//}.{extension}"
    archive_fmt = "{id}"

    def __init__(self, match):
        BaseExtractor.__init__(self, match)

        try:
            instance = INSTANCES[self.category]
        except KeyError:
            pass
        else:
            cookies = instance.get("cookies")
            if cookies:
                domain = self.root.rpartition("/")[2]
                self._update_cookies_dict(cookies, domain=domain)
            file_url = instance.get("file_url")
            if file_url:
                self.file_url_fmt = file_url

    def items(self):
        data = self.metadata()

        for post in self.posts():

            for key in ("id", "width", "height"):
                post[key] = text.parse_int(post[key])
            post["tags"] = text.unquote(post["tags"])
            post.update(data)

            url = post["file_url"]
            if "/index.php?" in url:
                post["filename"], _, post["extension"] = \
                    url.rpartition("/")[2].rpartition(".")
            else:
                text.nameext_from_url(url, post)

            yield Message.Directory, post
            yield Message.Url, url, post

    def metadata(self):
        """Return general metadata"""
        return ()

    def posts(self):
        """Return an iterable containing data of all relevant posts"""
        return ()


INSTANCES = {
    "mememuseum": {
        "root": "https://meme.museum",
        "pattern": r"meme\.museum",
    },
    "loudbooru": {
        "root": "https://loudbooru.com",
        "pattern": r"loudbooru\.com",
        "cookies": {"ui-tnc-agreed": "true"},
    },
    "giantessbooru": {
        "root": "https://giantessbooru.com",
        "pattern": r"giantessbooru\.com",
        "cookies": {"agreed": "true"},
    },
    "tentaclerape": {
        "root": "https://tentaclerape.net",
        "pattern": r"tentaclerape\.net",
    },
    "cavemanon": {
        "root": "https://booru.cavemanon.xyz",
        "pattern": r"booru\.cavemanon\.xyz",
        "file_url": "{0}/index.php?q=image/{2}.{4}"
    },
}

BASE_PATTERN = Shimmie2Extractor.update(INSTANCES) + r"/(?:index\.php\?q=)?"


class Shimmie2TagExtractor(Shimmie2Extractor):
    """Extractor for shimmie2 posts by tag search"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    file_url_fmt = "{}/_images/{}/{}%20-%20{}.{}"
    pattern = BASE_PATTERN + r"post/list/([^/?#]+)(?:/(\d+))?()"
    test = (
        ("https://meme.museum/post/list/animated/1", {
            "pattern": r"https://meme\.museum/_images/\w+/\d+%20-%20",
            "count": ">= 30"
        }),
        ("https://loudbooru.com/post/list/original_character/1", {
            "pattern": r"https://loudbooru\.com/_images/[0-9a-f]{32}/\d+",
            "range": "1-100",
            "count": 100,
        }),
        ("https://giantessbooru.com/post/list/smiling/1", {
            "pattern": r"https://giantessbooru\.com/_images/[0-9a-f]{32}/\d+",
            "range": "1-100",
            "count": 100,
        }),
        ("https://tentaclerape.net/post/list/comic/1", {
            "pattern": r"https://tentaclerape\.net/_images/[0-9a-f]{32}/\d+",
            "range": "1-100",
            "count": 100,
        }),
        ("https://booru.cavemanon.xyz/index.php?q=post/list/Amber/1", {
            "pattern": r"https://booru\.cavemanon\.xyz"
                       r"/index\.php\?q=image/\d+\.\w+",
            "range": "1-100",
            "count": 100,
        }),
    )

    def __init__(self, match):
        Shimmie2Extractor.__init__(self, match)
        lastindex = match.lastindex
        self.tags = text.unquote(match.group(lastindex-2))
        self.page = match.group(lastindex-1)

    def metadata(self):
        return {"search_tags": self.tags}

    def posts(self):
        pnum = text.parse_int(self.page, 1)
        file_url_fmt = self.file_url_fmt.format

        init = True
        mime = ""

        while True:
            url = "{}/post/list/{}/{}".format(self.root, self.tags, pnum)
            page = self.request(url).text
            extr = text.extract_from(page)

            if init:
                init = False
                has_mime = ("data-mime='" in page)
                has_pid = ("data-post-id='" in page)

            while True:
                if has_mime:
                    mime = extr("data-mime='", "'")
                if has_pid:
                    pid = extr("data-post-id='", "'")
                else:
                    pid = extr("href='/post/view/", "?")

                if not pid:
                    break

                tags, dimensions, size = extr("title='", "'").split(" // ")
                width, _, height = dimensions.partition("x")
                md5 = extr("/_thumbs/", "/")

                yield {
                    "file_url": file_url_fmt(
                        self.root, md5, pid, text.quote(tags),
                        mime.rpartition("/")[2] if mime else "jpg"),
                    "id": pid,
                    "md5": md5,
                    "tags": tags,
                    "width": width,
                    "height": height,
                    "size": text.parse_bytes(size[:-1]),
                }

            pnum += 1
            if not extr(">Next<", ">"):
                if not extr("/{}'>{}<".format(pnum, pnum), ">"):
                    return


class Shimmie2PostExtractor(Shimmie2Extractor):
    """Extractor for single shimmie2 posts"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"post/view/(\d+)"
    test = (
        ("https://meme.museum/post/view/10243", {
            "pattern": r"https://meme\.museum/_images/105febebcd5ca791ee332adc"
                       r"49971f78/10243%20-%20g%20beard%20open_source%20richar"
                       r"d_stallman%20stallman%20tagme%20text\.jpg",
            "content": "45565f3f141fc960a8ae1168b80e718a494c52d2",
            "keyword": {
                "extension": "jpg",
                "file_url": "https://meme.museum/_images/105febebcd5ca791ee332"
                            "adc49971f78/10243%20-%20g%20beard%20open_source%2"
                            "0richard_stallman%20stallman%20tagme%20text.jpg",
                "filename": "10243 - g beard open_source richard_stallman "
                            "stallman tagme text",
                "height": 451,
                "id": 10243,
                "md5": "105febebcd5ca791ee332adc49971f78",
                "size": 0,
                "subcategory": "post",
                "tags": "/g/ beard open_source "
                        "richard_stallman stallman tagme text",
                "width": 480,
            },
        }),
        ("https://loudbooru.com/post/view/33828", {
            "pattern": r"https://loudbooru\.com/_images/.+\.png",
            "content": "a4755f787ba23ae2aa297a46810f802ca9032739",
            "keyword": {
                "extension": "png",
                "file_url": "https://loudbooru.com/_images/ca2638d903c86e8337f"
                            "e9aeb4974be88/33828%20-%202020%20artist%3Astikyfi"
                            "nkaz%20character%3Alisa_loud%20cover%20fanfiction"
                            "%3Aplatz_eins%20frowning%20half-closed_eyes%20sol"
                            "o%20text%20title_card.png",
                "filename": "33828 - 2020 artist:stikyfinkaz character:lisa_"
                            "loud cover fanfiction:platz_eins frowning "
                            "half-closed_eyes solo text title_card",
                "height": 1920,
                "id": 33828,
                "md5": "ca2638d903c86e8337fe9aeb4974be88",
                "tags": "2020 artist:stikyfinkaz character:lisa_loud cover "
                        "fanfiction:platz_eins frowning half-closed_eyes "
                        "solo text title_card",
                "width": 1078,
            },
        }),
        ("https://giantessbooru.com/post/view/41", {
            "pattern": r"https://giantessbooru\.com/_images"
                       r"/3f67e1986496806b7b14ff3e82ac5af4/41\.jpg",
            "content": "79115ed309d1f4e82e7bead6948760e889139c91",
            "keyword": {
                "extension": "jpg",
                "file_url": "https://giantessbooru.com/_images"
                            "/3f67e1986496806b7b14ff3e82ac5af4/41.jpg",
                "filename": "41",
                "height": 0,
                "id": 41,
                "md5": "3f67e1986496806b7b14ff3e82ac5af4",
                "size": 0,
                "tags": "anime bare_midriff color drawing gentle giantess "
                        "karbo looking_at_tinies negeyari outdoors smiling "
                        "snake_girl white_hair",
                "width": 0


            },
        }),
        ("https://tentaclerape.net/post/view/10", {
            "pattern": r"https://tentaclerape\.net/\./index\.php"
                       r"\?q=/image/10\.jpg",
            "content": "d0fd8f0f6517a76cb5e23ba09f3844950bf2c516",
            "keyword": {
                "extension": "jpg",
                "file_url": "https://tentaclerape.net/./index.php"
                            "?q=/image/10.jpg",
                "filename": "10",
                "height": 427,
                "id": 10,
                "md5": "945db71eeccaef82ce44b77564260c0b",
                "size": 0,
                "subcategory": "post",
                "tags": "Deviant_Art Pet Tentacle artist_sche blonde_hair "
                        "blouse boots green_eyes highheels leash miniskirt "
                        "octopus schoolgirl white_skin willing",
                "width": 300,
            },
        }),
        # video
        ("https://tentaclerape.net/post/view/91267", {
            "pattern": r"https://tentaclerape\.net/\./index\.php"
                       r"\?q=/image/91267\.mp4",
        }),
        ("https://booru.cavemanon.xyz/index.php?q=post/view/8335", {
            "pattern": r"https://booru\.cavemanon\.xyz"
                       r"/index\.php\?q=image/8335\.png",
            "content": "7158f7e4abbbf143bad5835eb93dbe4d68c1d4ab",
            "keyword": {
                "extension": "png",
                "file_url": "https://booru.cavemanon.xyz"
                            "/index.php?q=image/8335.png",
                "filename": "8335",
                "height": 460,
                "id": 8335,
                "md5": "",
                "size": 0,
                "tags": "Color Fang",
                "width": 459,
            },
        }),
    )

    def __init__(self, match):
        Shimmie2Extractor.__init__(self, match)
        self.post_id = match.group(match.lastindex)

    def posts(self):
        url = "{}/post/view/{}".format(self.root, self.post_id)
        extr = text.extract_from(self.request(url).text)

        post = {
            "id"      : self.post_id,
            "tags"    : extr(": ", "<").partition(" - ")[0].rstrip(")"),
            "md5"     : extr("/_thumbs/", "/"),
            "file_url": self.root + (
                extr("id='main_image' src='", "'") or
                extr("<source src='", "'")),
            "width"   : extr("data-width=", " ").strip("\"'"),
            "height"  : extr("data-height=", ">").partition(
                " ")[0].strip("\"'"),
            "size"    : 0,
        }

        if not post["md5"]:
            post["md5"] = text.extr(post["file_url"], "/_images/", "/")

        return (post,)
