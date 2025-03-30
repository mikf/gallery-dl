# -*- coding: utf-8 -*-

# Copyright 2015-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.deviantart.com/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache, memcache
import collections
import mimetypes
import binascii
import time
import re

BASE_PATTERN = (
    r"(?:https?://)?(?:"
    r"(?:www\.)?(?:fx)?deviantart\.com/(?!watch/)([\w-]+)|"
    r"(?!www\.)([\w-]+)\.(?:fx)?deviantart\.com)"
)
DEFAULT_AVATAR = "https://a.deviantart.net/avatars/default.gif"


class DeviantartExtractor(Extractor):
    """Base class for deviantart extractors"""
    category = "deviantart"
    root = "https://www.deviantart.com"
    directory_fmt = ("{category}", "{username}")
    filename_fmt = "{category}_{index}_{title}.{extension}"
    cookies_domain = ".deviantart.com"
    cookies_names = ("auth", "auth_secure", "userinfo")
    _last_request = 0

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = (match.group(1) or match.group(2) or "").lower()
        self.offset = 0

    def _init(self):
        self.jwt = self.config("jwt", False)
        self.flat = self.config("flat", True)
        self.extra = self.config("extra", False)
        self.quality = self.config("quality", "100")
        self.original = self.config("original", True)
        self.previews = self.config("previews", False)
        self.intermediary = self.config("intermediary", True)
        self.comments_avatars = self.config("comments-avatars", False)
        self.comments = self.comments_avatars or self.config("comments", False)

        self.api = DeviantartOAuthAPI(self)
        self.eclipse_api = None
        self.group = False
        self._premium_cache = {}

        unwatch = self.config("auto-unwatch")
        if unwatch:
            self.unwatch = []
            self.finalize = self._unwatch_premium
        else:
            self.unwatch = None

        if self.quality:
            if self.quality == "png":
                self.quality = "-fullview.png?"
                self.quality_sub = re.compile(r"-fullview\.[a-z0-9]+\?").sub
            else:
                self.quality = ",q_{}".format(self.quality)
                self.quality_sub = re.compile(r",q_\d+").sub

        if isinstance(self.original, str) and \
                self.original.lower().startswith("image"):
            self.original = True
            self._update_content = self._update_content_image
        else:
            self._update_content = self._update_content_default

        if self.previews == "all":
            self.previews_images = self.previews = True
        else:
            self.previews_images = False

        journals = self.config("journals", "html")
        if journals == "html":
            self.commit_journal = self._commit_journal_html
        elif journals == "text":
            self.commit_journal = self._commit_journal_text
        else:
            self.commit_journal = None

    def request(self, url, **kwargs):
        if "fatal" not in kwargs:
            kwargs["fatal"] = False
        while True:
            response = Extractor.request(self, url, **kwargs)
            if response.status_code != 403 or \
                    b"Request blocked." not in response.content:
                return response
            self.wait(seconds=300, reason="CloudFront block")

    def skip(self, num):
        self.offset += num
        return num

    def login(self):
        if self.cookies_check(self.cookies_names):
            return True

        username, password = self._get_auth_info()
        if username:
            self.cookies_update(_login_impl(self, username, password))
            return True

    def items(self):
        if self.user:
            group = self.config("group", True)
            if group:
                user = _user_details(self, self.user)
                if user:
                    self.user = user["username"]
                    self.group = False
                elif group == "skip":
                    self.log.info("Skipping group '%s'", self.user)
                    raise exception.StopExtraction()
                else:
                    self.subcategory = "group-" + self.subcategory
                    self.group = True

        for deviation in self.deviations():
            if isinstance(deviation, tuple):
                url, data = deviation
                yield Message.Queue, url, data
                continue

            if deviation["is_deleted"]:
                # prevent crashing in case the deviation really is
                # deleted
                self.log.debug(
                    "Skipping %s (deleted)", deviation["deviationid"])
                continue

            tier_access = deviation.get("tier_access")
            if tier_access == "locked":
                self.log.debug(
                    "Skipping %s (access locked)", deviation["deviationid"])
                continue

            if "premium_folder_data" in deviation:
                data = self._fetch_premium(deviation)
                if not data:
                    continue
                deviation.update(data)

            self.prepare(deviation)
            yield Message.Directory, deviation

            if "content" in deviation:
                content = self._extract_content(deviation)
                yield self.commit(deviation, content)

            elif deviation["is_downloadable"]:
                content = self.api.deviation_download(deviation["deviationid"])
                deviation["is_original"] = True
                yield self.commit(deviation, content)

            if "videos" in deviation and deviation["videos"]:
                video = max(deviation["videos"],
                            key=lambda x: text.parse_int(x["quality"][:-1]))
                deviation["is_original"] = False
                yield self.commit(deviation, video)

            if "flash" in deviation:
                deviation["is_original"] = True
                yield self.commit(deviation, deviation["flash"])

            if self.commit_journal:
                journal = self._extract_journal(deviation)
                if journal:
                    if self.extra:
                        deviation["_journal"] = journal["html"]
                    deviation["is_original"] = True
                    yield self.commit_journal(deviation, journal)

            if self.comments_avatars:
                for comment in deviation["comments"]:
                    user = comment["user"]
                    name = user["username"].lower()
                    if user["usericon"] == DEFAULT_AVATAR:
                        self.log.debug(
                            "Skipping avatar of '%s' (default)", name)
                        continue
                    _user_details.update(name, user)

                    url = "{}/{}/avatar/".format(self.root, name)
                    comment["_extractor"] = DeviantartAvatarExtractor
                    yield Message.Queue, url, comment

            if self.previews and "preview" in deviation:
                preview = deviation["preview"]
                deviation["is_preview"] = True
                if self.previews_images:
                    yield self.commit(deviation, preview)
                else:
                    mtype = mimetypes.guess_type(
                        "a." + deviation["extension"], False)[0]
                    if mtype and not mtype.startswith("image/"):
                        yield self.commit(deviation, preview)
                del deviation["is_preview"]

            if not self.extra:
                continue

            # ref: https://www.deviantart.com
            #      /developers/http/v1/20210526/object/editor_text
            # the value of "features" is a JSON string with forward
            # slashes escaped
            text_content = \
                deviation["text_content"]["body"]["features"].replace(
                    "\\/", "/") if "text_content" in deviation else None
            for txt in (text_content, deviation.get("description"),
                        deviation.get("_journal")):
                if txt is None:
                    continue
                for match in DeviantartStashExtractor.pattern.finditer(txt):
                    url = text.ensure_http_scheme(match.group(0))
                    deviation["_extractor"] = DeviantartStashExtractor
                    yield Message.Queue, url, deviation

    def deviations(self):
        """Return an iterable containing all relevant Deviation-objects"""

    def prepare(self, deviation):
        """Adjust the contents of a Deviation-object"""
        if "index" not in deviation:
            try:
                if deviation["url"].startswith((
                    "https://www.deviantart.com/stash/", "https://sta.sh",
                )):
                    filename = deviation["content"]["src"].split("/")[5]
                    deviation["index_base36"] = filename.partition("-")[0][1:]
                    deviation["index"] = id_from_base36(
                        deviation["index_base36"])
                else:
                    deviation["index"] = text.parse_int(
                        deviation["url"].rpartition("-")[2])
            except KeyError:
                deviation["index"] = 0
                deviation["index_base36"] = "0"
        if "index_base36" not in deviation:
            deviation["index_base36"] = base36_from_id(deviation["index"])

        if self.user:
            deviation["username"] = self.user
            deviation["_username"] = self.user.lower()
        else:
            deviation["username"] = deviation["author"]["username"]
            deviation["_username"] = deviation["username"].lower()

        deviation["published_time"] = text.parse_int(
            deviation["published_time"])
        deviation["date"] = text.parse_timestamp(
            deviation["published_time"])

        if self.comments:
            deviation["comments"] = (
                self._extract_comments(deviation["deviationid"], "deviation")
                if deviation["stats"]["comments"] else ()
            )

        # filename metadata
        sub = re.compile(r"\W").sub
        deviation["filename"] = "".join((
            sub("_", deviation["title"].lower()), "_by_",
            sub("_", deviation["author"]["username"].lower()), "-d",
            deviation["index_base36"],
        ))

    @staticmethod
    def commit(deviation, target):
        url = target["src"]
        name = target.get("filename") or url
        target = target.copy()
        target["filename"] = deviation["filename"]
        deviation["target"] = target
        deviation["extension"] = target["extension"] = text.ext_from_url(name)
        if "is_original" not in deviation:
            deviation["is_original"] = ("/v1/" not in url)
        return Message.Url, url, deviation

    def _commit_journal_html(self, deviation, journal):
        title = text.escape(deviation["title"])
        url = deviation["url"]
        thumbs = deviation.get("thumbs") or deviation.get("files")
        html = journal["html"]
        shadow = SHADOW_TEMPLATE.format_map(thumbs[0]) if thumbs else ""

        if not html:
            self.log.warning("%s: Empty journal content", deviation["index"])

        if "css" in journal:
            css, cls = journal["css"], "withskin"
        elif html.startswith("<style"):
            css, _, html = html.partition("</style>")
            css = css.partition(">")[2]
            cls = "withskin"
        else:
            css, cls = "", "journal-green"

        if html.find('<div class="boxtop journaltop">', 0, 250) != -1:
            needle = '<div class="boxtop journaltop">'
            header = HEADER_CUSTOM_TEMPLATE.format(
                title=title, url=url, date=deviation["date"],
            )
        else:
            needle = '<div usr class="gr">'
            username = deviation["author"]["username"]
            urlname = deviation.get("username") or username.lower()
            header = HEADER_TEMPLATE.format(
                title=title,
                url=url,
                userurl="{}/{}/".format(self.root, urlname),
                username=username,
                date=deviation["date"],
            )

        if needle in html:
            html = html.replace(needle, header, 1)
        else:
            html = JOURNAL_TEMPLATE_HTML_EXTRA.format(header, html)

        html = JOURNAL_TEMPLATE_HTML.format(
            title=title, html=html, shadow=shadow, css=css, cls=cls)

        deviation["extension"] = "htm"
        return Message.Url, html, deviation

    def _commit_journal_text(self, deviation, journal):
        html = journal["html"]
        if not html:
            self.log.warning("%s: Empty journal content", deviation["index"])
        elif html.startswith("<style"):
            html = html.partition("</style>")[2]
        head, _, tail = html.rpartition("<script")
        content = "\n".join(
            text.unescape(text.remove_html(txt))
            for txt in (head or tail).split("<br />")
        )
        txt = JOURNAL_TEMPLATE_TEXT.format(
            title=deviation["title"],
            username=deviation["author"]["username"],
            date=deviation["date"],
            content=content,
        )

        deviation["extension"] = "txt"
        return Message.Url, txt, deviation

    def _extract_journal(self, deviation):
        if "excerpt" in deviation:
            # # empty 'html'
            #  return self.api.deviation_content(deviation["deviationid"])

            if "_page" in deviation:
                page = deviation["_page"]
                del deviation["_page"]
            else:
                page = self._limited_request(deviation["url"]).text

            # extract journal html from webpage
            html = text.extr(
                page,
                "<h2>Literature Text</h2></span><div>",
                "</div></section></div></div>")
            if html:
                return {"html": html}

            self.log.debug("%s: Failed to extract journal HTML from webpage. "
                           "Falling back to __INITIAL_STATE__ markup.",
                           deviation["index"])

            # parse __INITIAL_STATE__ as fallback
            state = util.json_loads(text.extr(
                page, 'window.__INITIAL_STATE__ = JSON.parse("', '");')
                .replace("\\\\", "\\").replace("\\'", "'").replace('\\"', '"'))
            deviations = state["@@entities"]["deviation"]
            content = deviations.popitem()[1]["textContent"]

            html = self._textcontent_to_html(deviation, content)
            if html:
                return {"html": html}
            return {"html": content["excerpt"].replace("\n", "<br />")}

        if "body" in deviation:
            return {"html": deviation.pop("body")}
        return None

    def _textcontent_to_html(self, deviation, content):
        html = content["html"]
        markup = html.get("markup")

        if not markup or markup[0] != "{":
            return markup

        if html["type"] == "tiptap":
            try:
                return self._tiptap_to_html(markup)
            except Exception as exc:
                self.log.debug("", exc_info=exc)
                self.log.error("%s: '%s: %s'", deviation["index"],
                               exc.__class__.__name__, exc)

        self.log.warning("%s: Unsupported '%s' markup.",
                         deviation["index"], html["type"])

    def _tiptap_to_html(self, markup):
        html = []

        html.append('<div data-editor-viewer="1" '
                    'class="_83r8m _2CKTq _3NjDa mDnFl">')
        data = util.json_loads(markup)
        for block in data["document"]["content"]:
            self._tiptap_process_content(html, block)
        html.append("</div>")

        return "".join(html)

    def _tiptap_process_content(self, html, content):
        type = content["type"]

        if type == "paragraph":
            children = content.get("content")
            if children:
                html.append('<p style="')

                attrs = content["attrs"]
                if "textAlign" in attrs:
                    html.append("text-align:")
                    html.append(attrs["textAlign"])
                    html.append(";")
                self._tiptap_process_indentation(html, attrs)
                html.append('">')

                for block in children:
                    self._tiptap_process_content(html, block)
                html.append("</p>")
            else:
                html.append('<p class="empty-p"><br/></p>')

        elif type == "text":
            self._tiptap_process_text(html, content)

        elif type == "heading":
            attrs = content["attrs"]
            level = str(attrs.get("level") or "3")

            html.append("<h")
            html.append(level)
            html.append(' style="text-align:')
            html.append(attrs.get("textAlign") or "left")
            html.append('">')
            html.append('<span style="')
            self._tiptap_process_indentation(html, attrs)
            html.append('">')
            self._tiptap_process_children(html, content)
            html.append("</span></h")
            html.append(level)
            html.append(">")

        elif type in ("listItem", "bulletList", "orderedList", "blockquote"):
            c = type[1]
            tag = (
                "li" if c == "i" else
                "ul" if c == "u" else
                "ol" if c == "r" else
                "blockquote"
            )
            html.append("<" + tag + ">")
            self._tiptap_process_children(html, content)
            html.append("</" + tag + ">")

        elif type == "anchor":
            attrs = content["attrs"]
            html.append('<a id="')
            html.append(attrs.get("id") or "")
            html.append('" data-testid="anchor"></a>')

        elif type == "hardBreak":
            html.append("<br/><br/>")

        elif type == "horizontalRule":
            html.append("<hr/>")

        elif type == "da-deviation":
            self._tiptap_process_deviation(html, content)

        elif type == "da-mention":
            user = content["attrs"]["user"]["username"]
            html.append('<a href="https://www.deviantart.com/')
            html.append(user.lower())
            html.append('" data-da-type="da-mention" data-user="">@<!-- -->')
            html.append(user)
            html.append('</a>')

        elif type == "da-gif":
            attrs = content["attrs"]
            width = str(attrs.get("width") or "")
            height = str(attrs.get("height") or "")
            url = text.escape(attrs.get("url") or "")

            html.append('<div data-da-type="da-gif" data-width="')
            html.append(width)
            html.append('" data-height="')
            html.append(height)
            html.append('" data-alignment="')
            html.append(attrs.get("alignment") or "")
            html.append('" data-url="')
            html.append(url)
            html.append('" class="t61qu"><video role="img" autoPlay="" '
                        'muted="" loop="" style="pointer-events:none" '
                        'controlsList="nofullscreen" playsInline="" '
                        'aria-label="gif" data-da-type="da-gif" width="')
            html.append(width)
            html.append('" height="')
            html.append(height)
            html.append('" src="')
            html.append(url)
            html.append('" class="_1Fkk6"></video></div>')

        elif type == "da-video":
            src = text.escape(content["attrs"].get("src") or "")
            html.append('<div data-testid="video" data-da-type="da-video" '
                        'data-src="')
            html.append(src)
            html.append('" class="_1Uxvs"><div data-canfs="yes" data-testid="v'
                        'ideo-inner" class="main-video" style="width:780px;hei'
                        'ght:438px"><div style="width:780px;height:438px">'
                        '<video src="')
            html.append(src)
            html.append('" style="width:100%;height:100%;" preload="auto" cont'
                        'rols=""></video></div></div></div>')

        else:
            self.log.warning("Unsupported content type '%s'", type)

    def _tiptap_process_text(self, html, content):
        marks = content.get("marks")
        if marks:
            close = []
            for mark in marks:
                type = mark["type"]
                if type == "link":
                    attrs = mark.get("attrs") or {}
                    html.append('<a href="')
                    html.append(text.escape(attrs.get("href") or ""))
                    if "target" in attrs:
                        html.append('" target="')
                        html.append(attrs["target"])
                    html.append('" rel="')
                    html.append(attrs.get("rel") or
                                "noopener noreferrer nofollow ugc")
                    html.append('">')
                    close.append("</a>")
                elif type == "bold":
                    html.append("<strong>")
                    close.append("</strong>")
                elif type == "italic":
                    html.append("<em>")
                    close.append("</em>")
                elif type == "underline":
                    html.append("<u>")
                    close.append("</u>")
                elif type == "strike":
                    html.append("<s>")
                    close.append("</s>")
                elif type == "textStyle" and len(mark) <= 1:
                    pass
                else:
                    self.log.warning("Unsupported text marker '%s'", type)
            close.reverse()
            html.append(text.escape(content["text"]))
            html.extend(close)
        else:
            html.append(text.escape(content["text"]))

    def _tiptap_process_children(self, html, content):
        children = content.get("content")
        if children:
            for block in children:
                self._tiptap_process_content(html, block)

    def _tiptap_process_indentation(self, html, attrs):
        itype = ("text-indent" if attrs.get("indentType") == "line" else
                 "margin-inline-start")
        isize = str((attrs.get("indentation") or 0) * 24)
        html.append(itype + ":" + isize + "px")

    def _tiptap_process_deviation(self, html, content):
        dev = content["attrs"]["deviation"]
        media = dev.get("media") or ()

        html.append('<div class="jjNX2">')
        html.append('<figure class="Qf-HY" data-da-type="da-deviation" '
                    'data-deviation="" '
                    'data-width="" data-link="" data-alignment="center">')

        if "baseUri" in media:
            url, formats = self._eclipse_media(media)
            full = formats["fullview"]

            html.append('<a href="')
            html.append(text.escape(dev["url"]))
            html.append('" class="_3ouD5" style="margin:0 auto;display:flex;'
                        'align-items:center;justify-content:center;'
                        'overflow:hidden;width:780px;height:')
            html.append(str(780 * full["h"] / full["w"]))
            html.append('px">')

            html.append('<img src="')
            html.append(text.escape(url))
            html.append('" alt="')
            html.append(text.escape(dev["title"]))
            html.append('" style="width:100%;max-width:100%;display:block"/>')
            html.append("</a>")

        elif "textContent" in dev:
            html.append('<div class="_32Hs4" style="width:350px">')

            html.append('<a href="')
            html.append(text.escape(dev["url"]))
            html.append('" class="_3ouD5">')

            html.append('''\
<section class="Q91qI aG7Yi" style="width:350px;height:313px">\
<div class="_16ECM _1xMkk" aria-hidden="true">\
<svg height="100%" viewBox="0 0 15 12" preserveAspectRatio="xMidYMin slice" \
fill-rule="evenodd">\
<linearGradient x1="87.8481761%" y1="16.3690766%" \
x2="45.4107524%" y2="71.4898596%" id="app-root-3">\
<stop stop-color="#00FF62" offset="0%"></stop>\
<stop stop-color="#3197EF" stop-opacity="0" offset="100%"></stop>\
</linearGradient>\
<text class="_2uqbc" fill="url(#app-root-3)" text-anchor="end" x="15" y="11">J\
</text></svg></div><div class="_1xz9u">Literature</div><h3 class="_2WvKD">\
''')
            html.append(text.escape(dev["title"]))
            html.append('</h3><div class="_2CPLm">')
            html.append(text.escape(dev["textContent"]["excerpt"]))
            html.append('</div></section></a></div>')

        html.append('</figure></div>')

    def _extract_content(self, deviation):
        content = deviation["content"]

        if self.original and deviation["is_downloadable"]:
            self._update_content(deviation, content)
            return content

        if self.jwt:
            self._update_token(deviation, content)
            return content

        if content["src"].startswith("https://images-wixmp-"):
            if self.intermediary and deviation["index"] <= 790677560:
                # https://github.com/r888888888/danbooru/issues/4069
                intermediary, count = re.subn(
                    r"(/f/[^/]+/[^/]+)/v\d+/.*",
                    r"/intermediary\1", content["src"], 1)
                if count:
                    deviation["is_original"] = False
                    deviation["_fallback"] = (content["src"],)
                    content["src"] = intermediary
            if self.quality:
                content["src"] = self.quality_sub(
                    self.quality, content["src"], 1)

        return content

    @staticmethod
    def _find_folder(folders, name, uuid):
        if uuid.isdecimal():
            match = re.compile(name.replace(
                "-", r"[^a-z0-9]+") + "$", re.IGNORECASE).match
            for folder in folders:
                if match(folder["name"]):
                    return folder
                elif folder.get("has_subfolders"):
                    for subfolder in folder["subfolders"]:
                        if match(subfolder["name"]):
                            return subfolder
        else:
            for folder in folders:
                if folder["folderid"] == uuid:
                    return folder
                elif folder.get("has_subfolders"):
                    for subfolder in folder["subfolders"]:
                        if subfolder["folderid"] == uuid:
                            return subfolder
        raise exception.NotFoundError("folder")

    def _folder_urls(self, folders, category, extractor):
        base = "{}/{}/{}/".format(self.root, self.user, category)
        for folder in folders:
            folder["_extractor"] = extractor
            url = "{}{}/{}".format(base, folder["folderid"], folder["name"])
            yield url, folder

    def _update_content_default(self, deviation, content):
        if "premium_folder_data" in deviation or deviation.get("is_mature"):
            public = False
        else:
            public = None

        data = self.api.deviation_download(deviation["deviationid"], public)
        content.update(data)
        deviation["is_original"] = True

    def _update_content_image(self, deviation, content):
        data = self.api.deviation_download(deviation["deviationid"])
        url = data["src"].partition("?")[0]
        mtype = mimetypes.guess_type(url, False)[0]
        if mtype and mtype.startswith("image/"):
            content.update(data)
            deviation["is_original"] = True

    def _update_token(self, deviation, content):
        """Replace JWT to be able to remove width/height limits

        All credit goes to @Ironchest337
        for discovering and implementing this method
        """
        url, sep, _ = content["src"].partition("/v1/")
        if not sep:
            return

        # 'images-wixmp' returns 401 errors, but just 'wixmp' still works
        url = url.replace("//images-wixmp", "//wixmp", 1)

        #  header = b'{"typ":"JWT","alg":"none"}'
        payload = (
            b'{"sub":"urn:app:","iss":"urn:app:","obj":[[{"path":"/f/' +
            url.partition("/f/")[2].encode() +
            b'"}]],"aud":["urn:service:file.download"]}'
        )

        deviation["_fallback"] = (content["src"],)
        deviation["is_original"] = True
        content["src"] = (
            "{}?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.{}.".format(
                url,
                #  base64 of 'header' is precomputed as 'eyJ0eX...'
                #  binascii.b2a_base64(header).rstrip(b"=\n").decode(),
                binascii.b2a_base64(payload).rstrip(b"=\n").decode())
        )

    def _extract_comments(self, target_id, target_type="deviation"):
        results = None
        comment_ids = [None]

        while comment_ids:
            comments = self.api.comments(
                target_id, target_type, comment_ids.pop())

            if results:
                results.extend(comments)
            else:
                results = comments

            # parent comments, i.e. nodes with at least one child
            parents = {c["parentid"] for c in comments}
            # comments with more than one reply
            replies = {c["commentid"] for c in comments if c["replies"]}
            # add comment UUIDs with replies that are not parent to any node
            comment_ids.extend(replies - parents)

        return results

    def _limited_request(self, url, **kwargs):
        """Limits HTTP requests to one every 2 seconds"""
        diff = time.time() - DeviantartExtractor._last_request
        if diff < 2.0:
            self.sleep(2.0 - diff, "request")
        response = self.request(url, **kwargs)
        DeviantartExtractor._last_request = time.time()
        return response

    def _fetch_premium(self, deviation):
        try:
            return self._premium_cache[deviation["deviationid"]]
        except KeyError:
            pass

        if not self.api.refresh_token_key:
            self.log.warning(
                "Unable to access premium content (no refresh-token)")
            self._fetch_premium = lambda _: None
            return None

        dev = self.api.deviation(deviation["deviationid"], False)
        folder = deviation["premium_folder_data"]
        username = dev["author"]["username"]

        # premium_folder_data is no longer present when user has access (#5063)
        has_access = ("premium_folder_data" not in dev) or folder["has_access"]

        if not has_access and folder["type"] == "watchers" and \
                self.config("auto-watch"):
            if self.unwatch is not None:
                self.unwatch.append(username)
            if self.api.user_friends_watch(username):
                has_access = True
                self.log.info(
                    "Watching %s for premium folder access", username)
            else:
                self.log.warning(
                    "Error when trying to watch %s. "
                    "Try again with a new refresh-token", username)

        if has_access:
            self.log.info("Fetching premium folder data")
        else:
            self.log.warning("Unable to access premium content (type: %s)",
                             folder["type"])

        cache = self._premium_cache
        for dev in self.api.gallery(
                username, folder["gallery_id"], public=False):
            cache[dev["deviationid"]] = dev if has_access else None

        return cache.get(deviation["deviationid"])

    def _unwatch_premium(self):
        for username in self.unwatch:
            self.log.info("Unwatching %s", username)
            self.api.user_friends_unwatch(username)

    def _eclipse_media(self, media, format="preview"):
        url = [media["baseUri"]]

        formats = {
            fmt["t"]: fmt
            for fmt in media["types"]
        }

        tokens = media.get("token") or ()
        if tokens:
            if len(tokens) <= 1:
                fmt = formats[format]
                if "c" in fmt:
                    url.append(fmt["c"].replace(
                        "<prettyName>", media["prettyName"]))
            url.append("?token=")
            url.append(tokens[-1])

        return "".join(url), formats

    def _eclipse_to_oauth(self, eclipse_api, deviations):
        for obj in deviations:
            deviation = obj["deviation"] if "deviation" in obj else obj
            deviation_uuid = eclipse_api.deviation_extended_fetch(
                deviation["deviationId"],
                deviation["author"]["username"],
                "journal" if deviation["isJournal"] else "art",
            )["deviation"]["extended"]["deviationUuid"]
            yield self.api.deviation(deviation_uuid)


class DeviantartUserExtractor(DeviantartExtractor):
    """Extractor for an artist's user profile"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/?$"
    example = "https://www.deviantart.com/USER"

    def initialize(self):
        pass

    skip = Extractor.skip

    def items(self):
        base = "{}/{}/".format(self.root, self.user)
        return self._dispatch_extractors((
            (DeviantartAvatarExtractor    , base + "avatar"),
            (DeviantartBackgroundExtractor, base + "banner"),
            (DeviantartGalleryExtractor   , base + "gallery"),
            (DeviantartScrapsExtractor    , base + "gallery/scraps"),
            (DeviantartJournalExtractor   , base + "posts"),
            (DeviantartStatusExtractor    , base + "posts/statuses"),
            (DeviantartFavoriteExtractor  , base + "favourites"),
        ), ("gallery",))


###############################################################################
# OAuth #######################################################################

class DeviantartGalleryExtractor(DeviantartExtractor):
    """Extractor for all deviations from an artist's gallery"""
    subcategory = "gallery"
    archive_fmt = "g_{_username}_{index}.{extension}"
    pattern = (BASE_PATTERN + r"/gallery"
               r"(?:/all|/recommended-for-you|/?\?catpath=)?/?$")
    example = "https://www.deviantart.com/USER/gallery/"

    def deviations(self):
        if self.flat and not self.group:
            return self.api.gallery_all(self.user, self.offset)
        folders = self.api.gallery_folders(self.user)
        return self._folder_urls(folders, "gallery", DeviantartFolderExtractor)


class DeviantartAvatarExtractor(DeviantartExtractor):
    """Extractor for an artist's avatar"""
    subcategory = "avatar"
    archive_fmt = "a_{_username}_{index}"
    pattern = BASE_PATTERN + r"/avatar"
    example = "https://www.deviantart.com/USER/avatar/"

    def deviations(self):
        name = self.user.lower()
        user = _user_details(self, name)
        if not user:
            return ()

        icon = user["usericon"]
        if icon == DEFAULT_AVATAR:
            self.log.debug("Skipping avatar of '%s' (default)", name)
            return ()

        _, sep, index = icon.rpartition("?")
        if not sep:
            index = "0"

        formats = self.config("formats")
        if not formats:
            url = icon.replace("/avatars/", "/avatars-big/", 1)
            return (self._make_deviation(url, user, index, ""),)

        if isinstance(formats, str):
            formats = formats.replace(" ", "").split(",")

        results = []
        for fmt in formats:
            fmt, _, ext = fmt.rpartition(".")
            if fmt:
                fmt = "-" + fmt
            url = "https://a.deviantart.net/avatars{}/{}/{}/{}.{}?{}".format(
                fmt, name[0], name[1], name, ext, index)
            results.append(self._make_deviation(url, user, index, fmt))
        return results

    def _make_deviation(self, url, user, index, fmt):
        return {
            "author"         : user,
            "da_category"    : "avatar",
            "index"          : text.parse_int(index),
            "is_deleted"     : False,
            "is_downloadable": False,
            "published_time" : 0,
            "title"          : "avatar" + fmt,
            "stats"          : {"comments": 0},
            "content"        : {"src": url},
        }


class DeviantartBackgroundExtractor(DeviantartExtractor):
    """Extractor for an artist's banner"""
    subcategory = "background"
    archive_fmt = "b_{index}"
    pattern = BASE_PATTERN + r"/ba(?:nner|ckground)"
    example = "https://www.deviantart.com/USER/banner/"

    def deviations(self):
        try:
            return (self.api.user_profile(self.user.lower())
                    ["cover_deviation"]["cover_deviation"],)
        except Exception:
            return ()


class DeviantartFolderExtractor(DeviantartExtractor):
    """Extractor for deviations inside an artist's gallery folder"""
    subcategory = "folder"
    directory_fmt = ("{category}", "{username}", "{folder[title]}")
    archive_fmt = "F_{folder[uuid]}_{index}.{extension}"
    pattern = BASE_PATTERN + r"/gallery/([^/?#]+)/([^/?#]+)"
    example = "https://www.deviantart.com/USER/gallery/12345/TITLE"

    def __init__(self, match):
        DeviantartExtractor.__init__(self, match)
        self.folder = None
        self.folder_id = match.group(3)
        self.folder_name = match.group(4)

    def deviations(self):
        folders = self.api.gallery_folders(self.user)
        folder = self._find_folder(folders, self.folder_name, self.folder_id)

        # Leaving this here for backwards compatibility
        self.folder = {
            "title": folder["name"],
            "uuid" : folder["folderid"],
            "index": self.folder_id,
            "owner": self.user,
            "parent_uuid": folder["parent"],
        }

        if folder.get("subfolder"):
            self.folder["parent_folder"] = folder["parent_folder"]
            self.archive_fmt = "F_{folder[parent_uuid]}_{index}.{extension}"

            if self.flat:
                self.directory_fmt = ("{category}", "{username}",
                                      "{folder[parent_folder]}")
            else:
                self.directory_fmt = ("{category}", "{username}",
                                      "{folder[parent_folder]}",
                                      "{folder[title]}")

        if folder.get("has_subfolders") and self.config("subfolders", True):
            for subfolder in folder["subfolders"]:
                subfolder["parent_folder"] = folder["name"]
                subfolder["subfolder"] = True
            yield from self._folder_urls(
                folder["subfolders"], "gallery", DeviantartFolderExtractor)

        yield from self.api.gallery(self.user, folder["folderid"], self.offset)

    def prepare(self, deviation):
        DeviantartExtractor.prepare(self, deviation)
        deviation["folder"] = self.folder


class DeviantartStashExtractor(DeviantartExtractor):
    """Extractor for sta.sh-ed deviations"""
    subcategory = "stash"
    archive_fmt = "{index}.{extension}"
    pattern = (r"(?:https?://)?(?:(?:www\.)?deviantart\.com/stash|sta\.s(h))"
               r"/([a-z0-9]+)")
    example = "https://www.deviantart.com/stash/abcde"

    skip = Extractor.skip

    def __init__(self, match):
        DeviantartExtractor.__init__(self, match)
        self.user = None

    def deviations(self, stash_id=None):
        if stash_id is None:
            legacy_url, stash_id = self.groups
        else:
            legacy_url = False

        if legacy_url and stash_id[0] == "2":
            url = "https://sta.sh/" + stash_id
            response = self._limited_request(url)
            stash_id = response.url.rpartition("/")[2]
            page = response.text
        else:
            url = "https://www.deviantart.com/stash/" + stash_id
            page = self._limited_request(url).text

        if stash_id[0] == "0":
            uuid = text.extr(page, '//deviation/', '"')
            if uuid:
                deviation = self.api.deviation(uuid)
                deviation["_page"] = page
                deviation["index"] = text.parse_int(text.extr(
                    page, '\\"deviationId\\":', ','))
                yield deviation
                return

        for sid in text.extract_iter(
                page, 'href="https://www.deviantart.com/stash/', '"'):
            if sid == stash_id or sid.endswith("#comments"):
                continue
            yield from self.deviations(sid)


class DeviantartFavoriteExtractor(DeviantartExtractor):
    """Extractor for an artist's favorites"""
    subcategory = "favorite"
    directory_fmt = ("{category}", "{username}", "Favourites")
    archive_fmt = "f_{_username}_{index}.{extension}"
    pattern = BASE_PATTERN + r"/favourites(?:/all|/?\?catpath=)?/?$"
    example = "https://www.deviantart.com/USER/favourites/"

    def deviations(self):
        if self.flat:
            return self.api.collections_all(self.user, self.offset)
        folders = self.api.collections_folders(self.user)
        return self._folder_urls(
            folders, "favourites", DeviantartCollectionExtractor)


class DeviantartCollectionExtractor(DeviantartExtractor):
    """Extractor for a single favorite collection"""
    subcategory = "collection"
    directory_fmt = ("{category}", "{username}", "Favourites",
                     "{collection[title]}")
    archive_fmt = "C_{collection[uuid]}_{index}.{extension}"
    pattern = BASE_PATTERN + r"/favourites/([^/?#]+)/([^/?#]+)"
    example = "https://www.deviantart.com/USER/favourites/12345/TITLE"

    def __init__(self, match):
        DeviantartExtractor.__init__(self, match)
        self.collection = None
        self.collection_id = match.group(3)
        self.collection_name = match.group(4)

    def deviations(self):
        folders = self.api.collections_folders(self.user)
        folder = self._find_folder(
            folders, self.collection_name, self.collection_id)
        self.collection = {
            "title": folder["name"],
            "uuid" : folder["folderid"],
            "index": self.collection_id,
            "owner": self.user,
        }
        return self.api.collections(self.user, folder["folderid"], self.offset)

    def prepare(self, deviation):
        DeviantartExtractor.prepare(self, deviation)
        deviation["collection"] = self.collection


class DeviantartJournalExtractor(DeviantartExtractor):
    """Extractor for an artist's journals"""
    subcategory = "journal"
    directory_fmt = ("{category}", "{username}", "Journal")
    archive_fmt = "j_{_username}_{index}.{extension}"
    pattern = BASE_PATTERN + r"/(?:posts(?:/journals)?|journal)/?(?:\?.*)?$"
    example = "https://www.deviantart.com/USER/posts/journals/"

    def deviations(self):
        return self.api.browse_user_journals(self.user, self.offset)


class DeviantartStatusExtractor(DeviantartExtractor):
    """Extractor for an artist's status updates"""
    subcategory = "status"
    directory_fmt = ("{category}", "{username}", "Status")
    filename_fmt = "{category}_{index}_{title}_{date}.{extension}"
    archive_fmt = "S_{_username}_{index}.{extension}"
    pattern = BASE_PATTERN + r"/posts/statuses"
    example = "https://www.deviantart.com/USER/posts/statuses/"

    def deviations(self):
        for status in self.api.user_statuses(self.user, self.offset):
            yield from self.status(status)

    def status(self, status):
        for item in status.get("items") or ():  # do not trust is_share
            # shared deviations/statuses
            if "deviation" in item:
                yield item["deviation"].copy()
            if "status" in item:
                yield from self.status(item["status"].copy())
        # assume is_deleted == true means necessary fields are missing
        if status["is_deleted"]:
            self.log.warning(
                "Skipping status %s (deleted)", status.get("statusid"))
            return
        yield status

    def prepare(self, deviation):
        if "deviationid" in deviation:
            return DeviantartExtractor.prepare(self, deviation)

        try:
            path = deviation["url"].split("/")
            deviation["index"] = text.parse_int(path[-1] or path[-2])
        except KeyError:
            deviation["index"] = 0

        if self.user:
            deviation["username"] = self.user
            deviation["_username"] = self.user.lower()
        else:
            deviation["username"] = deviation["author"]["username"]
            deviation["_username"] = deviation["username"].lower()

        deviation["date"] = dt = text.parse_datetime(deviation["ts"])
        deviation["published_time"] = int(util.datetime_to_timestamp(dt))

        deviation["da_category"] = "Status"
        deviation["category_path"] = "status"
        deviation["is_downloadable"] = False
        deviation["title"] = "Status Update"

        comments_count = deviation.pop("comments_count", 0)
        deviation["stats"] = {"comments": comments_count}
        if self.comments:
            deviation["comments"] = (
                self._extract_comments(deviation["statusid"], "status")
                if comments_count else ()
            )


class DeviantartTagExtractor(DeviantartExtractor):
    """Extractor for deviations from tag searches"""
    subcategory = "tag"
    directory_fmt = ("{category}", "Tags", "{search_tags}")
    archive_fmt = "T_{search_tags}_{index}.{extension}"
    pattern = r"(?:https?://)?www\.deviantart\.com/tag/([^/?#]+)"
    example = "https://www.deviantart.com/tag/TAG"

    def __init__(self, match):
        DeviantartExtractor.__init__(self, match)
        self.tag = text.unquote(match.group(1))

    def deviations(self):
        return self.api.browse_tags(self.tag, self.offset)

    def prepare(self, deviation):
        DeviantartExtractor.prepare(self, deviation)
        deviation["search_tags"] = self.tag


class DeviantartWatchExtractor(DeviantartExtractor):
    """Extractor for Deviations from watched users"""
    subcategory = "watch"
    pattern = (r"(?:https?://)?(?:www\.)?deviantart\.com"
               r"/(?:watch/deviations|notifications/watch)()()")
    example = "https://www.deviantart.com/watch/deviations"

    def deviations(self):
        return self.api.browse_deviantsyouwatch()


class DeviantartWatchPostsExtractor(DeviantartExtractor):
    """Extractor for Posts from watched users"""
    subcategory = "watch-posts"
    pattern = r"(?:https?://)?(?:www\.)?deviantart\.com/watch/posts()()"
    example = "https://www.deviantart.com/watch/posts"

    def deviations(self):
        return self.api.browse_posts_deviantsyouwatch()


###############################################################################
# Eclipse #####################################################################

class DeviantartDeviationExtractor(DeviantartExtractor):
    """Extractor for single deviations"""
    subcategory = "deviation"
    archive_fmt = "g_{_username}_{index}.{extension}"
    pattern = (BASE_PATTERN + r"/(art|journal)/(?:[^/?#]+-)?(\d+)"
               r"|(?:https?://)?(?:www\.)?(?:fx)?deviantart\.com/"
               r"(?:view/|deviation/|view(?:-full)?\.php/*\?(?:[^#]+&)?id=)"
               r"(\d+)"  # bare deviation ID without slug
               r"|(?:https?://)?fav\.me/d([0-9a-z]+)")  # base36
    example = "https://www.deviantart.com/UsER/art/TITLE-12345"

    skip = Extractor.skip

    def __init__(self, match):
        DeviantartExtractor.__init__(self, match)
        self.type = match.group(3)
        self.deviation_id = \
            match.group(4) or match.group(5) or id_from_base36(match.group(6))

    def deviations(self):
        if self.user:
            url = "{}/{}/{}/{}".format(
                self.root, self.user, self.type or "art", self.deviation_id)
        else:
            url = "{}/view/{}/".format(self.root, self.deviation_id)

        page = self._limited_request(url, notfound="deviation").text
        uuid = text.extr(page, '"deviationUuid\\":\\"', '\\')
        if not uuid:
            raise exception.NotFoundError("deviation")

        deviation = self.api.deviation(uuid)
        deviation["_page"] = page

        _dev_info = text.extr(
            page, '\\"deviationExtended\\":', ',\\"deviation\\":', None)
        # Clean up escaped quotes
        _json_str = re.sub(
            r'(?<!\\)\\{1}"', '"', _dev_info).replace("\\'", "'")
        _extended_info = util.json_loads(_json_str)[self.deviation_id]
        additional_media = _extended_info.get("additionalMedia") or ()

        if additional_media:
            self.filename_fmt = ("{category}_{index}_{index_file}_{title}_"
                                 "{num:>02}.{extension}")
            self.archive_fmt = ("g_{_username}_{index}{index_file:?_//}."
                                "{extension}")

        deviation["index_file"] = 0
        deviation["count"] = 1 + len(additional_media)
        deviation["num"] = 1
        yield deviation

        for index, post in enumerate(additional_media):
            uri = post["media"]["baseUri"].encode().decode("unicode-escape")
            deviation["content"]["src"] = uri
            deviation["num"] += 1
            deviation["index_file"] = post["fileId"]
            # Download only works on purchased materials - no way to check
            deviation["is_downloadable"] = False
            yield deviation


class DeviantartScrapsExtractor(DeviantartExtractor):
    """Extractor for an artist's scraps"""
    subcategory = "scraps"
    directory_fmt = ("{category}", "{username}", "Scraps")
    archive_fmt = "s_{_username}_{index}.{extension}"
    pattern = BASE_PATTERN + r"/gallery/(?:\?catpath=)?scraps\b"
    example = "https://www.deviantart.com/USER/gallery/scraps"

    def deviations(self):
        self.login()

        eclipse_api = DeviantartEclipseAPI(self)
        return self._eclipse_to_oauth(
            eclipse_api, eclipse_api.gallery_scraps(self.user, self.offset))


class DeviantartSearchExtractor(DeviantartExtractor):
    """Extractor for deviantart search results"""
    subcategory = "search"
    directory_fmt = ("{category}", "Search", "{search_tags}")
    archive_fmt = "Q_{search_tags}_{index}.{extension}"
    pattern = (r"(?:https?://)?www\.deviantart\.com"
               r"/search(?:/deviations)?/?\?([^#]+)")
    example = "https://www.deviantart.com/search?q=QUERY"
    skip = Extractor.skip

    def __init__(self, match):
        DeviantartExtractor.__init__(self, match)
        self.query = text.parse_query(self.user)
        self.search = self.query.get("q", "")
        self.user = ""

    def deviations(self):
        logged_in = self.login()

        eclipse_api = DeviantartEclipseAPI(self)
        search = (eclipse_api.search_deviations
                  if logged_in else self._search_html)
        return self._eclipse_to_oauth(eclipse_api, search(self.query))

    def prepare(self, deviation):
        DeviantartExtractor.prepare(self, deviation)
        deviation["search_tags"] = self.search

    def _search_html(self, params):
        url = self.root + "/search"

        while True:
            response = self.request(url, params=params)

            if response.history and "/users/login" in response.url:
                raise exception.StopExtraction("HTTP redirect to login page")
            page = response.text

            for dev in DeviantartDeviationExtractor.pattern.findall(
                    page)[2::3]:
                yield {
                    "deviationId": dev[3],
                    "author": {"username": dev[0]},
                    "isJournal": dev[2] == "journal",
                }

            cursor = text.extr(page, r'\"cursor\":\"', '\\',)
            if not cursor:
                return
            params["cursor"] = cursor


class DeviantartGallerySearchExtractor(DeviantartExtractor):
    """Extractor for deviantart gallery searches"""
    subcategory = "gallery-search"
    archive_fmt = "g_{_username}_{index}.{extension}"
    pattern = BASE_PATTERN + r"/gallery/?\?(q=[^#]+)"
    example = "https://www.deviantart.com/USER/gallery?q=QUERY"

    def __init__(self, match):
        DeviantartExtractor.__init__(self, match)
        self.query = match.group(3)

    def deviations(self):
        self.login()

        eclipse_api = DeviantartEclipseAPI(self)
        query = text.parse_query(self.query)
        self.search = query["q"]

        return self._eclipse_to_oauth(
            eclipse_api, eclipse_api.galleries_search(
                self.user,
                self.search,
                self.offset,
                query.get("sort", "most-recent"),
            ))

    def prepare(self, deviation):
        DeviantartExtractor.prepare(self, deviation)
        deviation["search_tags"] = self.search


class DeviantartFollowingExtractor(DeviantartExtractor):
    """Extractor for user's watched users"""
    subcategory = "following"
    pattern = BASE_PATTERN + "/(?:about#)?watching"
    example = "https://www.deviantart.com/USER/about#watching"

    def items(self):
        api = DeviantartOAuthAPI(self)

        for user in api.user_friends(self.user):
            url = "{}/{}".format(self.root, user["user"]["username"])
            user["_extractor"] = DeviantartUserExtractor
            yield Message.Queue, url, user


###############################################################################
# API Interfaces ##############################################################

class DeviantartOAuthAPI():
    """Interface for the DeviantArt OAuth API

    https://www.deviantart.com/developers/http/v1/20160316
    """
    CLIENT_ID = "5388"
    CLIENT_SECRET = "76b08c69cfb27f26d6161f9ab6d061a1"

    def __init__(self, extractor):
        self.extractor = extractor
        self.log = extractor.log
        self.headers = {"dA-minor-version": "20210526"}
        self._warn_429 = True

        self.delay = extractor.config("wait-min", 0)
        self.delay_min = max(2, self.delay)

        self.mature = extractor.config("mature", "true")
        if not isinstance(self.mature, str):
            self.mature = "true" if self.mature else "false"

        self.strategy = extractor.config("pagination")
        self.folders = extractor.config("folders", False)
        self.public = extractor.config("public", True)

        client_id = extractor.config("client-id")
        if client_id:
            self.client_id = str(client_id)
            self.client_secret = extractor.config("client-secret")
        else:
            self.client_id = self.CLIENT_ID
            self.client_secret = self.CLIENT_SECRET

        token = extractor.config("refresh-token")
        if token is None or token == "cache":
            token = "#" + self.client_id
            if not _refresh_token_cache(token):
                token = None
        self.refresh_token_key = token

        metadata = extractor.config("metadata", False)
        if not metadata:
            metadata = True if extractor.extra else False
        if metadata:
            self.metadata = True

            if isinstance(metadata, str):
                if metadata == "all":
                    metadata = ("submission", "camera", "stats",
                                "collection", "gallery")
                else:
                    metadata = metadata.replace(" ", "").split(",")
            elif not isinstance(metadata, (list, tuple)):
                metadata = ()

            self._metadata_params = {"mature_content": self.mature}
            self._metadata_public = None
            if metadata:
                # extended metadata
                self.limit = 10
                for param in metadata:
                    self._metadata_params["ext_" + param] = "1"
                if "ext_collection" in self._metadata_params or \
                        "ext_gallery" in self._metadata_params:
                    if token:
                        self._metadata_public = False
                    else:
                        self.log.error("'collection' and 'gallery' metadata "
                                       "require a refresh token")
            else:
                # base metadata
                self.limit = 50
        else:
            self.metadata = False
            self.limit = None

        self.log.debug(
            "Using %s API credentials (client-id %s)",
            "default" if self.client_id == self.CLIENT_ID else "custom",
            self.client_id,
        )

    def browse_deviantsyouwatch(self, offset=0):
        """Yield deviations from users you watch"""
        endpoint = "/browse/deviantsyouwatch"
        params = {"limit": 50, "offset": offset,
                  "mature_content": self.mature}
        return self._pagination(endpoint, params, public=False)

    def browse_posts_deviantsyouwatch(self, offset=0):
        """Yield posts from users you watch"""
        endpoint = "/browse/posts/deviantsyouwatch"
        params = {"limit": 50, "offset": offset,
                  "mature_content": self.mature}
        return self._pagination(endpoint, params, public=False, unpack=True)

    def browse_tags(self, tag, offset=0):
        """ Browse a tag """
        endpoint = "/browse/tags"
        params = {
            "tag"           : tag,
            "offset"        : offset,
            "limit"         : 50,
            "mature_content": self.mature,
        }
        return self._pagination(endpoint, params)

    def browse_user_journals(self, username, offset=0):
        journals = filter(
            lambda post: "/journal/" in post["url"],
            self.user_profile_posts(username))
        if offset:
            journals = util.advance(journals, offset)
        return journals

    def collections(self, username, folder_id, offset=0):
        """Yield all Deviation-objects contained in a collection folder"""
        endpoint = "/collections/" + folder_id
        params = {"username": username, "offset": offset, "limit": 24,
                  "mature_content": self.mature}
        return self._pagination(endpoint, params)

    def collections_all(self, username, offset=0):
        """Yield all deviations in a user's collection"""
        endpoint = "/collections/all"
        params = {"username": username, "offset": offset, "limit": 24,
                  "mature_content": self.mature}
        return self._pagination(endpoint, params)

    @memcache(keyarg=1)
    def collections_folders(self, username, offset=0):
        """Yield all collection folders of a specific user"""
        endpoint = "/collections/folders"
        params = {"username": username, "offset": offset, "limit": 50,
                  "mature_content": self.mature}
        return self._pagination_list(endpoint, params)

    def comments(self, target_id, target_type="deviation",
                 comment_id=None, offset=0):
        """Fetch comments posted on a target"""
        endpoint = "/comments/{}/{}".format(target_type, target_id)
        params = {
            "commentid"     : comment_id,
            "maxdepth"      : "5",
            "offset"        : offset,
            "limit"         : 50,
            "mature_content": self.mature,
        }
        return self._pagination_list(endpoint, params=params, key="thread")

    def deviation(self, deviation_id, public=None):
        """Query and return info about a single Deviation"""
        endpoint = "/deviation/" + deviation_id

        deviation = self._call(endpoint, public=public)
        if deviation.get("is_mature") and public is None and \
                self.refresh_token_key:
            deviation = self._call(endpoint, public=False)

        if self.metadata:
            self._metadata((deviation,))
        if self.folders:
            self._folders((deviation,))
        return deviation

    def deviation_content(self, deviation_id, public=None):
        """Get extended content of a single Deviation"""
        endpoint = "/deviation/content"
        params = {"deviationid": deviation_id}
        content = self._call(endpoint, params=params, public=public)
        if public and content["html"].startswith(
                '        <span class=\"username-with-symbol'):
            if self.refresh_token_key:
                content = self._call(endpoint, params=params, public=False)
            else:
                self.log.warning("Private Journal")
        return content

    def deviation_download(self, deviation_id, public=None):
        """Get the original file download (if allowed)"""
        endpoint = "/deviation/download/" + deviation_id
        params = {"mature_content": self.mature}

        try:
            return self._call(
                endpoint, params=params, public=public, log=False)
        except Exception:
            if not self.refresh_token_key:
                raise
            return self._call(endpoint, params=params, public=False)

    def deviation_metadata(self, deviations):
        """ Fetch deviation metadata for a set of deviations"""
        endpoint = "/deviation/metadata?" + "&".join(
            "deviationids[{}]={}".format(num, deviation["deviationid"])
            for num, deviation in enumerate(deviations)
        )
        return self._call(
            endpoint,
            params=self._metadata_params,
            public=self._metadata_public,
        )["metadata"]

    def gallery(self, username, folder_id, offset=0, extend=True, public=None):
        """Yield all Deviation-objects contained in a gallery folder"""
        endpoint = "/gallery/" + folder_id
        params = {"username": username, "offset": offset, "limit": 24,
                  "mature_content": self.mature, "mode": "newest"}
        return self._pagination(endpoint, params, extend, public)

    def gallery_all(self, username, offset=0):
        """Yield all Deviation-objects of a specific user"""
        endpoint = "/gallery/all"
        params = {"username": username, "offset": offset, "limit": 24,
                  "mature_content": self.mature}
        return self._pagination(endpoint, params)

    @memcache(keyarg=1)
    def gallery_folders(self, username, offset=0):
        """Yield all gallery folders of a specific user"""
        endpoint = "/gallery/folders"
        params = {"username": username, "offset": offset, "limit": 50,
                  "mature_content": self.mature}
        return self._pagination_list(endpoint, params)

    def user_friends(self, username, offset=0):
        """Get the users list of friends"""
        endpoint = "/user/friends/" + username
        params = {"limit": 50, "offset": offset, "mature_content": self.mature}
        return self._pagination(endpoint, params)

    def user_friends_watch(self, username):
        """Watch a user"""
        endpoint = "/user/friends/watch/" + username
        data = {
            "watch[friend]"       : "0",
            "watch[deviations]"   : "0",
            "watch[journals]"     : "0",
            "watch[forum_threads]": "0",
            "watch[critiques]"    : "0",
            "watch[scraps]"       : "0",
            "watch[activity]"     : "0",
            "watch[collections]"  : "0",
            "mature_content"      : self.mature,
        }
        return self._call(
            endpoint, method="POST", data=data, public=False, fatal=False,
        ).get("success")

    def user_friends_unwatch(self, username):
        """Unwatch a user"""
        endpoint = "/user/friends/unwatch/" + username
        return self._call(
            endpoint, method="POST", public=False, fatal=False,
        ).get("success")

    @memcache(keyarg=1)
    def user_profile(self, username):
        """Get user profile information"""
        endpoint = "/user/profile/" + username
        return self._call(endpoint, fatal=False)

    def user_profile_posts(self, username):
        endpoint = "/user/profile/posts"
        params = {"username": username, "limit": 50,
                  "mature_content": self.mature}
        return self._pagination(endpoint, params)

    def user_statuses(self, username, offset=0):
        """Yield status updates of a specific user"""
        statuses = filter(
            lambda post: "/status-update/" in post["url"],
            self.user_profile_posts(username))
        if offset:
            statuses = util.advance(statuses, offset)
        return statuses

    def authenticate(self, refresh_token_key):
        """Authenticate the application by requesting an access token"""
        self.headers["Authorization"] = \
            self._authenticate_impl(refresh_token_key)

    @cache(maxage=3600, keyarg=1)
    def _authenticate_impl(self, refresh_token_key):
        """Actual authenticate implementation"""
        url = "https://www.deviantart.com/oauth2/token"
        if refresh_token_key:
            self.log.info("Refreshing private access token")
            data = {"grant_type": "refresh_token",
                    "refresh_token": _refresh_token_cache(refresh_token_key)}
        else:
            self.log.info("Requesting public access token")
            data = {"grant_type": "client_credentials"}

        auth = util.HTTPBasicAuth(self.client_id, self.client_secret)
        response = self.extractor.request(
            url, method="POST", data=data, auth=auth, fatal=False)
        data = response.json()

        if response.status_code != 200:
            self.log.debug("Server response: %s", data)
            raise exception.AuthenticationError('"{}" ({})'.format(
                data.get("error_description"), data.get("error")))
        if refresh_token_key:
            _refresh_token_cache.update(
                refresh_token_key, data["refresh_token"])
        return "Bearer " + data["access_token"]

    def _call(self, endpoint, fatal=True, log=True, public=None, **kwargs):
        """Call an API endpoint"""
        url = "https://www.deviantart.com/api/v1/oauth2" + endpoint
        kwargs["fatal"] = None

        if public is None:
            public = self.public

        while True:
            if self.delay:
                self.extractor.sleep(self.delay, "api")

            self.authenticate(None if public else self.refresh_token_key)
            kwargs["headers"] = self.headers
            response = self.extractor.request(url, **kwargs)

            try:
                data = response.json()
            except ValueError:
                self.log.error("Unable to parse API response")
                data = {}

            status = response.status_code
            if 200 <= status < 400:
                if self.delay > self.delay_min:
                    self.delay -= 1
                return data
            if not fatal and status != 429:
                return None

            error = data.get("error_description")
            if error == "User not found.":
                raise exception.NotFoundError("user or group")
            if error == "Deviation not downloadable.":
                raise exception.AuthorizationError()

            self.log.debug(response.text)
            msg = "API responded with {} {}".format(
                status, response.reason)
            if status == 429:
                if self.delay < 30:
                    self.delay += 1
                self.log.warning("%s. Using %ds delay.", msg, self.delay)

                if self._warn_429 and self.delay >= 3:
                    self._warn_429 = False
                    if self.client_id == self.CLIENT_ID:
                        self.log.info(
                            "Register your own OAuth application and use its "
                            "credentials to prevent this error: "
                            "https://gdl-org.github.io/docs/configuration.html"
                            "#extractor-deviantart-client-id-client-secret")
            else:
                if log:
                    self.log.error(msg)
                return data

    def _should_switch_tokens(self, results, params):
        if len(results) < params["limit"]:
            return True

        if not self.extractor.jwt:
            for item in results:
                if item.get("is_mature"):
                    return True

        return False

    def _pagination(self, endpoint, params,
                    extend=True, public=None, unpack=False, key="results"):
        warn = True
        if public is None:
            public = self.public

        if self.limit and params["limit"] > self.limit:
            params["limit"] = (params["limit"] // self.limit) * self.limit

        while True:
            data = self._call(endpoint, params=params, public=public)
            try:
                results = data[key]
            except KeyError:
                self.log.error("Unexpected API response: %s", data)
                return

            if unpack:
                results = [item["journal"] for item in results
                           if "journal" in item]
            if extend:
                if public and self._should_switch_tokens(results, params):
                    if self.refresh_token_key:
                        self.log.debug("Switching to private access token")
                        public = False
                        continue
                    elif data["has_more"] and warn:
                        warn = False
                        self.log.warning(
                            "Private or mature deviations detected! "
                            "Run 'gallery-dl oauth:deviantart' and follow the "
                            "instructions to be able to access them.")

                # "statusid" cannot be used instead
                if results and "deviationid" in results[0]:
                    if self.metadata:
                        self._metadata(results)
                    if self.folders:
                        self._folders(results)
                else:  # attempt to fix "deleted" deviations
                    for dev in self._shared_content(results):
                        if not dev["is_deleted"]:
                            continue
                        patch = self._call(
                            "/deviation/" + dev["deviationid"], fatal=False)
                        if patch:
                            dev.update(patch)

            yield from results

            if not data["has_more"] and (
                    self.strategy != "manual" or not results or not extend):
                return

            if "next_cursor" in data:
                if not data["next_cursor"]:
                    return
                params["offset"] = None
                params["cursor"] = data["next_cursor"]
            elif data["next_offset"] is not None:
                params["offset"] = data["next_offset"]
                params["cursor"] = None
            else:
                if params.get("offset") is None:
                    return
                params["offset"] = int(params["offset"]) + len(results)

    def _pagination_list(self, endpoint, params, key="results"):
        result = []
        result.extend(self._pagination(endpoint, params, False, key=key))
        return result

    @staticmethod
    def _shared_content(results):
        """Return an iterable of shared deviations in 'results'"""
        for result in results:
            for item in result.get("items") or ():
                if "deviation" in item:
                    yield item["deviation"]

    def _metadata(self, deviations):
        """Add extended metadata to each deviation object"""
        if len(deviations) <= self.limit:
            self._metadata_batch(deviations)
        else:
            n = self.limit
            for index in range(0, len(deviations), n):
                self._metadata_batch(deviations[index:index+n])

    def _metadata_batch(self, deviations):
        """Fetch extended metadata for a single batch of deviations"""
        for deviation, metadata in zip(
                deviations, self.deviation_metadata(deviations)):
            deviation.update(metadata)
            deviation["tags"] = [t["tag_name"] for t in deviation["tags"]]

    def _folders(self, deviations):
        """Add a list of all containing folders to each deviation object"""
        for deviation in deviations:
            deviation["folders"] = self._folders_map(
                deviation["author"]["username"])[deviation["deviationid"]]

    @memcache(keyarg=1)
    def _folders_map(self, username):
        """Generate a deviation_id -> folders mapping for 'username'"""
        self.log.info("Collecting folder information for '%s'", username)
        folders = self.gallery_folders(username)

        # create 'folderid'-to-'folder' mapping
        fmap = {
            folder["folderid"]: folder
            for folder in folders
        }

        # add parent names to folders, but ignore "Featured" as parent
        featured = folders[0]["folderid"]
        done = False

        while not done:
            done = True
            for folder in folders:
                parent = folder["parent"]
                if not parent:
                    pass
                elif parent == featured:
                    folder["parent"] = None
                else:
                    parent = fmap[parent]
                    if parent["parent"]:
                        done = False
                    else:
                        folder["name"] = parent["name"] + "/" + folder["name"]
                        folder["parent"] = None

        # map deviationids to folder names
        dmap = collections.defaultdict(list)
        for folder in folders:
            for deviation in self.gallery(
                    username, folder["folderid"], 0, False):
                dmap[deviation["deviationid"]].append(folder["name"])
        return dmap


class DeviantartEclipseAPI():
    """Interface to the DeviantArt Eclipse API"""

    def __init__(self, extractor):
        self.extractor = extractor
        self.log = extractor.log
        self.request = self.extractor._limited_request
        self.csrf_token = None

    def deviation_extended_fetch(self, deviation_id, user, kind=None):
        endpoint = "/_puppy/dadeviation/init"
        params = {
            "deviationid"     : deviation_id,
            "username"        : user,
            "type"            : kind,
            "include_session" : "false",
            "expand"          : "deviation.related",
            "da_minor_version": "20230710",
        }
        return self._call(endpoint, params)

    def gallery_scraps(self, user, offset=0):
        endpoint = "/_puppy/dashared/gallection/contents"
        params = {
            "username"     : user,
            "type"         : "gallery",
            "offset"       : offset,
            "limit"        : 24,
            "scraps_folder": "true",
        }
        return self._pagination(endpoint, params)

    def galleries_search(self, user, query, offset=0, order="most-recent"):
        endpoint = "/_puppy/dashared/gallection/search"
        params = {
            "username": user,
            "type"    : "gallery",
            "order"   : order,
            "q"       : query,
            "offset"  : offset,
            "limit"   : 24,
        }
        return self._pagination(endpoint, params)

    def search_deviations(self, params):
        endpoint = "/_puppy/dabrowse/search/deviations"
        return self._pagination(endpoint, params, key="deviations")

    def user_info(self, user, expand=False):
        endpoint = "/_puppy/dauserprofile/init/about"
        params = {"username": user}
        return self._call(endpoint, params)

    def user_watching(self, user, offset=0):
        gruserid, moduleid = self._ids_watching(user)

        endpoint = "/_puppy/gruser/module/watching"
        params = {
            "gruserid"     : gruserid,
            "gruser_typeid": "4",
            "username"     : user,
            "moduleid"     : moduleid,
            "offset"       : offset,
            "limit"        : 24,
        }
        return self._pagination(endpoint, params)

    def _call(self, endpoint, params):
        url = "https://www.deviantart.com" + endpoint
        params["csrf_token"] = self.csrf_token or self._fetch_csrf_token()

        response = self.request(url, params=params, fatal=None)

        try:
            return response.json()
        except Exception:
            return {"error": response.text}

    def _pagination(self, endpoint, params, key="results"):
        limit = params.get("limit", 24)
        warn = True

        while True:
            data = self._call(endpoint, params)

            results = data.get(key)
            if results is None:
                return
            if len(results) < limit and warn and data.get("hasMore"):
                warn = False
                self.log.warning(
                    "Private deviations detected! "
                    "Provide login credentials or session cookies "
                    "to be able to access them.")
            yield from results

            if not data.get("hasMore"):
                return

            if "nextCursor" in data:
                params["offset"] = None
                params["cursor"] = data["nextCursor"]
            elif "nextOffset" in data:
                params["offset"] = data["nextOffset"]
                params["cursor"] = None
            elif params.get("offset") is None:
                return
            else:
                params["offset"] = int(params["offset"]) + len(results)

    def _ids_watching(self, user):
        url = "{}/{}/about".format(self.extractor.root, user)
        page = self.request(url).text

        gruser_id = text.extr(page, ' data-userid="', '"')

        pos = page.find('\\"name\\":\\"watching\\"')
        if pos < 0:
            raise exception.NotFoundError("'watching' module ID")
        module_id = text.rextract(
            page, '\\"id\\":', ',', pos)[0].strip('" ')

        self._fetch_csrf_token(page)
        return gruser_id, module_id

    def _fetch_csrf_token(self, page=None):
        if page is None:
            page = self.request(self.extractor.root + "/").text
        self.csrf_token = token = text.extr(
            page, "window.__CSRF_TOKEN__ = '", "'")
        return token


@memcache(keyarg=1)
def _user_details(extr, name):
    try:
        return extr.api.user_profile(name)["user"]
    except Exception:
        return None


@cache(maxage=36500*86400, keyarg=0)
def _refresh_token_cache(token):
    if token and token[0] == "#":
        return None
    return token


@cache(maxage=28*86400, keyarg=1)
def _login_impl(extr, username, password):
    extr.log.info("Logging in as %s", username)

    url = "https://www.deviantart.com/users/login"
    page = extr.request(url).text

    data = {}
    for item in text.extract_iter(page, '<input type="hidden" name="', '"/>'):
        name, _, value = item.partition('" value="')
        data[name] = value

    challenge = data.get("challenge")
    if challenge and challenge != "0":
        extr.log.warning("Login requires solving a CAPTCHA")
        extr.log.debug(challenge)

    data["username"] = username
    data["password"] = password
    data["remember"] = "on"

    extr.sleep(2.0, "login")
    url = "https://www.deviantart.com/_sisu/do/signin"
    response = extr.request(url, method="POST", data=data)

    if not response.history:
        raise exception.AuthenticationError()

    return {
        cookie.name: cookie.value
        for cookie in extr.cookies
    }


def id_from_base36(base36):
    return util.bdecode(base36, _ALPHABET)


def base36_from_id(deviation_id):
    return util.bencode(int(deviation_id), _ALPHABET)


_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"


###############################################################################
# Journal Formats #############################################################

SHADOW_TEMPLATE = """
<span class="shadow">
    <img src="{src}" class="smshadow" width="{width}" height="{height}">
</span>
<br><br>
"""

HEADER_TEMPLATE = """<div usr class="gr">
<div class="metadata">
    <h2><a href="{url}">{title}</a></h2>
    <ul>
        <li class="author">
            by <span class="name"><span class="username-with-symbol u">
            <a class="u regular username" href="{userurl}">{username}</a>\
<span class="user-symbol regular"></span></span></span>,
            <span>{date}</span>
        </li>
    </ul>
</div>
"""

HEADER_CUSTOM_TEMPLATE = """<div class='boxtop journaltop'>
<h2>
    <img src="https://st.deviantart.net/minish/gruzecontrol/icons/journal.gif\
?2" style="vertical-align:middle" alt=""/>
    <a href="{url}">{title}</a>
</h2>
Journal Entry: <span>{date}</span>
"""

JOURNAL_TEMPLATE_HTML = """text:<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <link rel="stylesheet" href="https://st.deviantart.net\
/css/deviantart-network_lc.css?3843780832"/>
    <link rel="stylesheet" href="https://st.deviantart.net\
/css/group_secrets_lc.css?3250492874"/>
    <link rel="stylesheet" href="https://st.deviantart.net\
/css/v6core_lc.css?4246581581"/>
    <link rel="stylesheet" href="https://st.deviantart.net\
/css/sidebar_lc.css?1490570941"/>
    <link rel="stylesheet" href="https://st.deviantart.net\
/css/writer_lc.css?3090682151"/>
    <link rel="stylesheet" href="https://st.deviantart.net\
/css/v6loggedin_lc.css?3001430805"/>
    <style>{css}</style>
    <link rel="stylesheet" href="https://st.deviantart.net\
/roses/cssmin/core.css?1488405371919"/>
    <link rel="stylesheet" href="https://st.deviantart.net\
/roses/cssmin/peeky.css?1487067424177"/>
    <link rel="stylesheet" href="https://st.deviantart.net\
/roses/cssmin/desktop.css?1491362542749"/>
    <link rel="stylesheet" href="https://static.parastorage.com/services\
/da-deviation/2bfd1ff7a9d6bf10d27b98dd8504c0399c3f9974a015785114b7dc6b\
/app.min.css"/>
</head>
<body id="deviantART-v7" class="bubble no-apps loggedout w960 deviantart">
    <div id="output">
    <div class="dev-page-container bubbleview">
    <div class="dev-page-view view-mode-normal">
    <div class="dev-view-main-content">
    <div class="dev-view-deviation">
    {shadow}
    <div class="journal-wrapper tt-a">
    <div class="journal-wrapper2">
    <div class="journal {cls} journalcontrol">
    {html}
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
</body>
</html>
"""

JOURNAL_TEMPLATE_HTML_EXTRA = """\
<div id="devskin0"><div class="negate-box-margin" style="">\
<div usr class="gr-box gr-genericbox"
        ><i usr class="gr1"><i></i></i
        ><i usr class="gr2"><i></i></i
        ><i usr class="gr3"><i></i></i
        ><div usr class="gr-top">
            <i usr class="tri"></i>
            {}
            </div>
    </div><div usr class="gr-body"><div usr class="gr">
            <div class="grf-indent">
            <div class="text">
                {}            </div>
        </div>
                </div></div>
        <i usr class="gr3 gb"></i>
        <i usr class="gr2 gb"></i>
        <i usr class="gr1 gb gb1"></i>    </div>
    </div></div>"""

JOURNAL_TEMPLATE_TEXT = """text:{title}
by {username}, {date}

{content}
"""
