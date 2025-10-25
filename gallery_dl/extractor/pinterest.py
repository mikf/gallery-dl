# -*- coding: utf-8 -*-

# Copyright 2016-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.pinterest.com/"""

from .common import Extractor, Message
from .. import text, exception
import itertools

BASE_PATTERN = r"(?:https?://)?(?:\w+\.)?pinterest\.[\w.]+"


class PinterestExtractor(Extractor):
    """Base class for pinterest extractors"""
    category = "pinterest"
    filename_fmt = "{category}_{id}{media_id|page_id:?_//}.{extension}"
    archive_fmt = "{id}{media_id|page_id}"
    root = "https://www.pinterest.com"

    def _init(self):
        domain = self.config("domain")
        if not domain or domain == "auto" :
            self.root = text.root_from_url(self.url)
        else:
            self.root = text.ensure_http_scheme(domain)

        self.api = self.utils().PinterestAPI(self)
        self.stories = self.config("stories", True)
        self.videos = self.config("videos", True)

    def items(self):
        data = self.metadata()

        for pin in self.pins():

            if isinstance(pin, tuple):
                url, data = pin
                yield Message.Queue, url, data
                continue

            try:
                files = self._extract_files(pin)
            except Exception as exc:
                self.log.traceback(exc)
                self.log.warning(
                    "%s: Error when extracting download URLs (%s: %s)",
                    pin.get("id"), exc.__class__.__name__, exc)
                continue

            pin.update(data)
            pin["count"] = len(files)

            for key in (
                "description",
                "closeup_description",
                "closeup_unified_description",
            ):
                if value := pin.get(key):
                    pin[key] = value.strip()

            yield Message.Directory, pin
            for pin["num"], file in enumerate(files, 1):
                url = file["url"]
                text.nameext_from_url(url, pin)
                pin.update(file)

                if "media_id" not in file:
                    pin["media_id"] = ""
                if "page_id" not in file:
                    pin["page_id"] = ""

                if pin["extension"] == "m3u8":
                    url = "ytdl:" + url
                    pin["_ytdl_manifest"] = "hls"
                    pin["extension"] = "mp4"

                yield Message.Url, url, pin

    def metadata(self):
        """Return general metadata"""

    def pins(self):
        """Return all relevant pin objects"""

    def _extract_files(self, pin):
        story_pin_data = pin.get("story_pin_data")
        if story_pin_data and self.stories:
            return self._extract_story(pin, story_pin_data)

        if carousel_data := pin.get("carousel_data"):
            return self._extract_carousel(pin, carousel_data)

        videos = pin.get("videos")
        if videos and self.videos:
            return (self._extract_video(videos),)

        try:
            return (pin["images"]["orig"],)
        except Exception:
            self.log.debug("%s: No files found", pin.get("id"))
            return ()

    def _extract_story(self, pin, story):
        files = []
        story_id = story.get("id")

        for page in story["pages"]:
            page_id = page.get("id")

            for block in page["blocks"]:
                type = block.get("type")

                if type == "story_pin_image_block":
                    if 1 == len(page["blocks"]) == len(story["pages"]):
                        try:
                            media = pin["images"]["orig"]
                        except Exception:
                            media = self._extract_image(page, block)
                    else:
                        media = self._extract_image(page, block)

                elif type == "story_pin_video_block" or "video" in block:
                    video = block["video"]
                    media = self._extract_video(video)
                    media["media_id"] = video.get("id") or ""

                elif type == "story_pin_music_block" or "audio" in block:
                    media = block["audio"]
                    media["url"] = media["audio_url"]
                    media["media_id"] = media.get("id") or ""

                elif type == "story_pin_paragraph_block":
                    media = {"url": "text:" + block["text"],
                             "extension": "txt",
                             "media_id": block.get("id")}

                elif type == "story_pin_product_sticker_block":
                    continue

                elif type == "story_pin_static_sticker_block":
                    continue

                else:
                    self.log.warning("%s: Unsupported story block '%s'",
                                     pin.get("id"), type)
                    try:
                        media = self._extract_image(page, block)
                    except Exception:
                        continue

                media["story_id"] = story_id
                media["page_id"] = page_id
                files.append(media)

        return files

    def _extract_carousel(self, pin, carousel_data):
        files = []
        for slot in carousel_data["carousel_slots"]:
            size, image = next(iter(slot["images"].items()))
            slot["media_id"] = slot.pop("id")
            slot["url"] = image["url"].replace(
                "/" + size + "/", "/originals/", 1)
            files.append(slot)
        return files

    def _extract_image(self, page, block):
        sig = block.get("image_signature") or page["image_signature"]
        url_base = (f"https://i.pinimg.com/originals"
                    f"/{sig[0:2]}/{sig[2:4]}/{sig[4:6]}/{sig}.")
        url_jpg = url_base + "jpg"
        url_png = url_base + "png"
        url_webp = url_base + "webp"

        try:
            media = block["image"]["images"]["originals"]
        except Exception:
            media = {"url": url_jpg, "_fallback": (url_png, url_webp,)}

        if media["url"] == url_jpg:
            media["_fallback"] = (url_png, url_webp,)
        else:
            media["_fallback"] = (url_jpg, url_png, url_webp,)
        media["media_id"] = sig

        return media

    def _extract_video(self, video):
        video_formats = video["video_list"]
        for fmt in ("V_HLSV4", "V_HLSV3_WEB", "V_HLSV3_MOBILE"):
            if fmt in video_formats:
                media = video_formats[fmt]
                break
        else:
            media = max(video_formats.values(),
                        key=lambda x: x.get("width", 0))
        if "V_720P" in video_formats:
            media["_fallback"] = (video_formats["V_720P"]["url"],)
        return media


class PinterestUserExtractor(PinterestExtractor):
    """Extractor for a user's boards"""
    subcategory = "user"
    pattern = rf"{BASE_PATTERN}/(?!pin/)([^/?#]+)(?:/_saved)?/?$"
    example = "https://www.pinterest.com/USER/"

    def __init__(self, match):
        PinterestExtractor.__init__(self, match)
        self.user = text.unquote(match[1])

    def items(self):
        for board in self.api.boards(self.user):
            if url := board.get("url"):
                board["_extractor"] = PinterestBoardExtractor
                yield Message.Queue, self.root + url, board


class PinterestAllpinsExtractor(PinterestExtractor):
    """Extractor for a user's 'All Pins' feed"""
    subcategory = "allpins"
    directory_fmt = ("{category}", "{user}")
    pattern = rf"{BASE_PATTERN}/(?!pin/)([^/?#]+)/pins/?$"
    example = "https://www.pinterest.com/USER/pins/"

    def __init__(self, match):
        PinterestExtractor.__init__(self, match)
        self.user = text.unquote(match[1])

    def metadata(self):
        return {"user": self.user}

    def pins(self):
        return self.api.user_pins(self.user)


class PinterestCreatedExtractor(PinterestExtractor):
    """Extractor for a user's created pins"""
    subcategory = "created"
    directory_fmt = ("{category}", "{user}")
    pattern = rf"{BASE_PATTERN}/(?!pin/)([^/?#]+)/_created/?$"
    example = "https://www.pinterest.com/USER/_created/"

    def __init__(self, match):
        PinterestExtractor.__init__(self, match)
        self.user = text.unquote(match[1])

    def metadata(self):
        return {"user": self.user}

    def pins(self):
        return self.api.user_activity_pins(self.user)


class PinterestSectionExtractor(PinterestExtractor):
    """Extractor for board sections on pinterest.com"""
    subcategory = "section"
    directory_fmt = ("{category}", "{board[owner][username]}",
                     "{board[name]}", "{section[title]}")
    archive_fmt = "{board[id]}_{id}"
    pattern = rf"{BASE_PATTERN}/(?!pin/)([^/?#]+)/([^/?#]+)/([^/?#]+)"
    example = "https://www.pinterest.com/USER/BOARD/SECTION"

    def __init__(self, match):
        PinterestExtractor.__init__(self, match)
        self.user = text.unquote(match[1])
        self.board_slug = text.unquote(match[2])
        self.section_slug = text.unquote(match[3])
        self.section = None

    def metadata(self):
        if self.section_slug.startswith("id:"):
            section = self.section = self.api.board_section(
                self.section_slug[3:])
        else:
            section = self.section = self.api.board_section_by_name(
                self.user, self.board_slug, self.section_slug)
        section.pop("preview_pins", None)
        return {"board": section.pop("board"), "section": section}

    def pins(self):
        return self.api.board_section_pins(self.section["id"])


class PinterestSearchExtractor(PinterestExtractor):
    """Extractor for Pinterest search results"""
    subcategory = "search"
    directory_fmt = ("{category}", "Search", "{search}")
    pattern = rf"{BASE_PATTERN}/search/pins/?\?q=([^&#]+)"
    example = "https://www.pinterest.com/search/pins/?q=QUERY"

    def __init__(self, match):
        PinterestExtractor.__init__(self, match)
        self.search = text.unquote(match[1])

    def metadata(self):
        return {"search": self.search}

    def pins(self):
        return self.api.search(self.search)


class PinterestPinExtractor(PinterestExtractor):
    """Extractor for images from a single pin from pinterest.com"""
    subcategory = "pin"
    pattern = rf"{BASE_PATTERN}/pin/([^/?#]+)(?!.*#related$)"
    example = "https://www.pinterest.com/pin/12345/"

    def __init__(self, match):
        PinterestExtractor.__init__(self, match)
        self.pin_id = match[1]
        self.pin = None

    def metadata(self):
        self.pin = self.api.pin(self.pin_id)
        return self.pin

    def pins(self):
        return (self.pin,)


class PinterestBoardExtractor(PinterestExtractor):
    """Extractor for images from a board from pinterest.com"""
    subcategory = "board"
    directory_fmt = ("{category}", "{board[owner][username]}", "{board[name]}")
    archive_fmt = "{board[id]}_{id}"
    pattern = (rf"{BASE_PATTERN}/(?!pin/)([^/?#]+)"
               r"/([^/?#]+)/?(?!.*#related$)")
    example = "https://www.pinterest.com/USER/BOARD/"

    def __init__(self, match):
        PinterestExtractor.__init__(self, match)
        self.user = text.unquote(match[1])
        self.board_name = text.unquote(match[2])
        self.board = None

    def metadata(self):
        self.board = self.api.board(self.user, self.board_name)
        return {"board": self.board}

    def pins(self):
        board = self.board
        pins = self.api.board_pins(board["id"])

        if board["section_count"] and self.config("sections", True):
            base = f"{self.root}{board['url']}id:"
            data = {"_extractor": PinterestSectionExtractor}
            sections = [(base + section["id"], data)
                        for section in self.api.board_sections(board["id"])]
            pins = itertools.chain(pins, sections)

        return pins


class PinterestRelatedPinExtractor(PinterestPinExtractor):
    """Extractor for related pins of another pin from pinterest.com"""
    subcategory = "related-pin"
    directory_fmt = ("{category}", "related {original_pin[id]}")
    pattern = rf"{BASE_PATTERN}/pin/([^/?#]+).*#related$"
    example = "https://www.pinterest.com/pin/12345/#related"

    def metadata(self):
        return {"original_pin": self.api.pin(self.pin_id)}

    def pins(self):
        return self.api.pin_related(self.pin_id)


class PinterestRelatedBoardExtractor(PinterestBoardExtractor):
    """Extractor for related pins of a board from pinterest.com"""
    subcategory = "related-board"
    directory_fmt = ("{category}", "{board[owner][username]}",
                     "{board[name]}", "related")
    pattern = rf"{BASE_PATTERN}/(?!pin/)([^/?#]+)/([^/?#]+)/?#related$"
    example = "https://www.pinterest.com/USER/BOARD/#related"

    def pins(self):
        return self.api.board_content_recommendation(self.board["id"])


class PinterestPinitExtractor(PinterestExtractor):
    """Extractor for images from a pin.it URL"""
    subcategory = "pinit"
    pattern = r"(?:https?://)?pin\.it/([^/?#]+)"
    example = "https://pin.it/abcde"

    def items(self):
        url = (f"https://api.pinterest.com/url_shortener"
               f"/{self.groups[0]}/redirect/")
        location = self.request_location(url)
        if not location:
            raise exception.NotFoundError("pin")
        elif PinterestPinExtractor.pattern.match(location):
            yield Message.Queue, location, {
                "_extractor": PinterestPinExtractor}
        elif PinterestBoardExtractor.pattern.match(location):
            yield Message.Queue, location, {
                "_extractor": PinterestBoardExtractor}
        else:
            raise exception.NotFoundError("pin")
