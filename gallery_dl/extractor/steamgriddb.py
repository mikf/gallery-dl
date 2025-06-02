# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.steamgriddb.com"""

from .common import Extractor, Message
from .. import text, exception


BASE_PATTERN = r"(?:https?://)?(?:www\.)?steamgriddb\.com"
LANGUAGE_CODES = (
    "aa", "ab", "ae", "af", "ak", "am", "an", "ar", "as", "av", "ay", "az",
    "ba", "be", "bg", "bh", "bi", "bm", "bn", "bo", "br", "bs", "ca", "ce",
    "ch", "co", "cr", "cs", "cu", "cv", "cy", "da", "de", "dv", "dz", "ee",
    "el", "en", "eo", "es", "et", "eu", "fa", "ff", "fi", "fj", "fo", "fr",
    "fy", "ga", "gd", "gl", "gn", "gu", "gv", "ha", "he", "hi", "ho", "hr",
    "ht", "hu", "hy", "hz", "ia", "id", "ie", "ig", "ii", "ik", "io", "is",
    "it", "iu", "ja", "jv", "ka", "kg", "ki", "kj", "kk", "kl", "km", "kn",
    "ko", "kr", "ks", "ku", "kv", "kw", "ky", "la", "lb", "lg", "li", "ln",
    "lo", "lt", "lu", "lv", "mg", "mh", "mi", "mk", "ml", "mn", "mr", "ms",
    "mt", "my", "na", "nb", "nd", "ne", "ng", "nl", "nn", "no", "nr", "nv",
    "ny", "oc", "oj", "om", "or", "os", "pa", "pi", "pl", "ps", "pt", "qu",
    "rm", "rn", "ro", "ru", "rw", "sa", "sc", "sd", "se", "sg", "si", "sk",
    "sl", "sm", "sn", "so", "sq", "sr", "ss", "st", "su", "sv", "sw", "ta",
    "te", "tg", "th", "ti", "tk", "tl", "tn", "to", "tr", "ts", "tt", "tw",
    "ty", "ug", "uk", "ur", "uz", "ve", "vi", "vo", "wa", "wo", "xh", "yi",
    "yo", "za", "zh", "zu",
)
FILE_EXT_TO_MIME = {
    "png": "image/png",
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
    "webp": "image/webp",
    "ico": "image/vnd.microsoft.icon",
    "all": "all",
}


class SteamgriddbExtractor(Extractor):
    """Base class for SteamGridDB"""
    category = "steamgriddb"
    directory_fmt = ("{category}", "{subcategory}", "{game[id]}")
    filename_fmt = "{game[id]}_{id}_{num:>02}.{extension}"
    archive_fmt = "{filename}"
    root = "https://www.steamgriddb.com"

    def _init(self):
        self.cookies_update({
            "userprefs": "%7B%22adult%22%3Afalse%7D",
        })

    def items(self):
        download_fake_png = self.config("download-fake-png", True)

        for asset in self.assets():
            fake_png = download_fake_png and asset.get("fake_png")

            asset["count"] = 2 if fake_png else 1
            yield Message.Directory, asset

            asset["num"] = 1
            url = asset["url"]
            yield Message.Url, url, text.nameext_from_url(url, asset)

            if fake_png:
                asset["num"] = 2
                asset["_http_adjust_extension"] = False
                url = fake_png
                yield Message.Url, url, text.nameext_from_url(url, asset)

    def _call(self, endpoint, **kwargs):
        data = self.request(self.root + endpoint, **kwargs).json()
        if not data["success"]:
            raise exception.StopExtraction(data["error"])
        return data["data"]


class SteamgriddbAssetsExtractor(SteamgriddbExtractor):
    """Base class for extracting a list of assets"""

    def __init__(self, match):
        SteamgriddbExtractor.__init__(self, match)
        list_type = match.group(1)
        id = int(match.group(2))
        self.game_id = id if list_type == "game" else None
        self.collection_id = id if list_type == "collection" else None
        self.page = int(match.group(3) or 1)

    def assets(self):
        limit = 48
        page = min(self.page - 1, 0)

        sort = self.config("sort", "score_desc")
        if sort not in ("score_desc", "score_asc", "score_old_desc",
                        "score_old_asc", "age_desc", "age_asc"):
            raise exception.StopExtractor("Invalid sort '%s'", sort)

        json = {
            "static"  : self.config("static", True),
            "animated": self.config("animated", True),
            "humor"   : self.config("humor", True),
            "nsfw"    : self.config("nsfw", True),
            "epilepsy": self.config("epilepsy", True),
            "untagged": self.config("untagged", True),

            "asset_type": self.asset_type,
            "limit": limit,
            "order": sort,
        }
        if self.valid_dimensions:
            json["dimensions"] = self.config_list(
                "dimensions", "dimension", self.valid_dimensions)
        json["styles"] = self.config_list("styles", "style", self.valid_styles)
        json["languages"] = self.config_list(
            "languages", "language", LANGUAGE_CODES)
        file_types = self.config_list(
            "file-types", "file type", self.valid_file_types)
        json["mime"] = [FILE_EXT_TO_MIME[i] for i in file_types]

        if self.game_id:
            json["game_id"] = [self.game_id]
        else:
            json["collection_id"] = self.collection_id

        while True:
            json["page"] = page

            data = self._call(
                "/api/public/search/assets", method="POST", json=json)
            for asset in data["assets"]:
                if not asset.get("game"):
                    asset["game"] = data["game"]
                yield asset

            if data["total"] <= limit * page:
                break
            page += 1

    def config_list(self, key, type_name, valid_values):
        value = self.config(key)
        if isinstance(value, str):
            value = value.split(",")

        if value is None or "all" in value:
            return ["all"]

        for i in value:
            if i not in valid_values:
                raise exception.StopExtraction("Invalid %s '%s'", type_name, i)

        return value


class SteamgriddbAssetExtractor(SteamgriddbExtractor):
    """Extractor for a single asset"""
    subcategory = "asset"
    pattern = BASE_PATTERN + r"/(grid|hero|logo|icon)/(\d+)"
    example = "https://www.steamgriddb.com/grid/1234"

    def __init__(self, match):
        SteamgriddbExtractor.__init__(self, match)
        self.asset_type = match.group(1)
        self.asset_id = match.group(2)

    def assets(self):
        endpoint = "/api/public/asset/" + self.asset_type + "/" + self.asset_id
        asset = self._call(endpoint)["asset"]
        if asset is None:
            raise exception.NotFoundError("asset ({}:{})".format(
                self.asset_type, self.asset_id))
        return (asset,)


class SteamgriddbGridsExtractor(SteamgriddbAssetsExtractor):
    subcategory = "grids"
    asset_type = "grid"
    pattern = BASE_PATTERN + r"/(game|collection)/(\d+)/grids(?:/(\d+))?"
    example = "https://www.steamgriddb.com/game/1234/grids"
    valid_dimensions = ("460x215", "920x430", "600x900", "342x482", "660x930",
                        "512x512", "1024x1024")
    valid_styles = ("alternate", "blurred", "no_logo", "material",
                    "white_logo")
    valid_file_types = ("png", "jpeg", "jpg", "webp")


class SteamgriddbHeroesExtractor(SteamgriddbAssetsExtractor):
    subcategory = "heroes"
    asset_type = "hero"
    pattern = BASE_PATTERN + r"/(game|collection)/(\d+)/heroes(?:/(\d+))?"
    example = "https://www.steamgriddb.com/game/1234/heroes"
    valid_dimensions = ("1920x620", "3840x1240", "1600x650")
    valid_styles = ("alternate", "blurred", "material")
    valid_file_types = ("png", "jpeg", "jpg", "webp")


class SteamgriddbLogosExtractor(SteamgriddbAssetsExtractor):
    subcategory = "logos"
    asset_type = "logo"
    pattern = BASE_PATTERN + r"/(game|collection)/(\d+)/logos(?:/(\d+))?"
    example = "https://www.steamgriddb.com/game/1234/logos"
    valid_dimensions = None
    valid_styles = ("official", "white", "black", "custom")
    valid_file_types = ("png", "webp")


class SteamgriddbIconsExtractor(SteamgriddbAssetsExtractor):
    subcategory = "icons"
    asset_type = "icon"
    pattern = BASE_PATTERN + r"/(game|collection)/(\d+)/icons(?:/(\d+))?"
    example = "https://www.steamgriddb.com/game/1234/icons"
    valid_dimensions = ["{0}x{0}".format(i) for i in (8, 10, 14, 16, 20, 24,
                        28, 32, 35, 40, 48, 54, 56, 57, 60, 64, 72, 76, 80, 90,
                        96, 100, 114, 120, 128, 144, 150, 152, 160, 180, 192,
                        194, 256, 310, 512, 768, 1024)]
    valid_styles = ("official", "custom")
    valid_file_types = ("png", "ico")
