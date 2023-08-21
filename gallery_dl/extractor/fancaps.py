# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://fancaps.net/"""

from .common import Extractor, Message
from .. import text
import re

SKIP_FIRST_N_IMAGES = 4
ANIME_BASE_PATTERN = r"(?:https?://)?(?:www\.)?fancaps\.net/anime/"
MOVIE_BASE_PATTERN = r"(?:https?://)?(?:www\.)?fancaps\.net/movies/"
TV_BASE_PATTERN = r"(?:https?://)?(?:www\.)?fancaps\.net/tv/"
ID_PATTERN = r"(\d{1,5})(-[a-zA-Z0-9_/]*)*"


def extract_episode(page):
    title_content = text.extr(
        page,
        '<h1 class="post_title" style="margin:0px;padding:7px;">',
        "</h1>"
    ).strip()
    return {
        "episode": (
            f'Episode {re.search(r"Episode (.+)", title_content).group(1)}'
        ),
        "episode_alt": text.extr(
            page, '<span style="color:#777;">Other Title: ', "</span>"
        ).replace("&nbsp;", " "),
    }


def id_groups_to_str(groups):
    return groups[0] + (groups[1] if len(groups) > 1 else "")


class FancapsAnimeEpisodeExtractor(Extractor):
    """Extractor for an anime episode on fancaps.net"""

    category = "fancaps"
    subcategory = "anime-episode"
    directory_fmt = ("{category}", "{series}", "{episode_id} {episode}")
    filename_fmt = "{image_id}.{extension}"
    archive_fmt = "{episode_id}"
    root = "https://fancaps.net/anime/episodeimages.php?"
    pattern = ANIME_BASE_PATTERN + rf"episodeimages\.php\?{ID_PATTERN}"
    test = (
        (
            "https://fancaps.net/anime/episodeimages.php?19879-Mushoku_Tensei"
            "__Jobless_Reincarnation/Episode_1"
        ),
        ("https://fancaps.net/anime/episodeimages.php?36394-"),
        (
            "https://fancaps.net/anime/episodeimages.php?33225"
            "-Bocchi_the_Rock/Episode_1"
        ),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        groups = match.groups()
        self.episode_url = self.root + id_groups_to_str(groups)
        self.episode_id = groups[0]
        self._base_original = "https://cdni.fancaps.net" \
            "/file/fancaps-animeimages/"
        self._base_fallback = (
            "https://ancdn.fancaps.net/",
            "https://animethumbs.fancaps.net/",
        )

    def metadata(self, page):
        series_match = re.search(
            r"<a href=\"https://fancaps\.net/anime/showimages\.php" +
            rf"\?{ID_PATTERN}\">",
            page,
        )
        return {
            "episode_id": self.episode_id,
            **extract_episode(page),
            "series": text.split_html(
                text.extr(page, series_match[0], "</a>")
            )[0],
            "series_url": (
                "https://fancaps.net/anime/episodeimages.php?"
                "id_groups_to_str(series_match.groups())"
            )
        }

    def _image_fallback(self, filename):
        for base_url in self._base_fallback:
            yield base_url + filename

    def items(self):
        true_episode_url = self.request(
            text.ensure_http_scheme(self.episode_url)
        ).url
        page_idx = 1
        metadata = None
        while True:
            page = self.request(f"{true_episode_url}&page={page_idx}").text
            if metadata is None:
                metadata = self.metadata(page)

            image_ids_gen = text.extract_iter(
                page, '<a href="https://fancaps.net/anime/picture.php?/', '"'
            )

            # First 4 images are top images of an episode
            for _ in range(SKIP_FIRST_N_IMAGES):
                next(image_ids_gen, None)

            is_last_page = True
            for image_id in image_ids_gen:
                is_last_page = False
                yield Message.Directory, metadata
                filename = f"{image_id}.jpg"
                yield Message.Url, self._base_original + filename, {
                    "_fallback": self._image_fallback(filename),
                    "image_id": image_id,
                    "extension": "jpg",
                }

            if is_last_page:
                break
            page_idx += 1


class FancapsAnimeSeriesExtractor(Extractor):
    """Extractor for an anime series on fancaps.net"""

    category = "fancaps"
    subcategory = "anime-series"
    root = "https://fancaps.net/anime/showimages.php?"
    pattern = ANIME_BASE_PATTERN + rf"showimages\.php\?{ID_PATTERN}"
    test = (("https://fancaps.net/anime/showimages.php?34868-Spy_Classroom"),)

    def __init__(self, match):
        Extractor.__init__(self, match)
        groups = match.groups()
        self.series_url = self.root + id_groups_to_str(groups)
        self.series_id = groups[0]

    def items(self):
        true_series_url = self.request(
            text.ensure_http_scheme(self.series_url)
        ).url
        page_idx = 1
        while True:
            page = self.request(f"{true_series_url}&page={page_idx}").text
            for episode_id in text.extract_iter(
                page,
                '<a href="https://fancaps.net/anime/episodeimages.php?',
                '" class="btn btn-block"',
            ):
                yield Message.Queue, (
                    "https://fancaps.net/anime/episodeimages.php"
                    f"?{episode_id}"
                ), {
                    "_extractor": FancapsAnimeEpisodeExtractor
                }

            if re.search('<a href="#">Next', page) is not None:
                break

            page_idx += 1


class FancapsTvEpisodeExtractor(Extractor):
    """Extractor for a TV episode on fancaps.net"""

    category = "fancaps"
    subcategory = "tv-episode"
    directory_fmt = ("{category}", "{series}", "{episode_id} {episode}")
    filename_fmt = "{image_id}.{extension}"
    archive_fmt = "{episode_id}"
    root = "https://fancaps.net/tv/episodeimages.php?"
    pattern = TV_BASE_PATTERN + rf"episodeimages\.php\?{ID_PATTERN}"
    test = (
        (
            "https://fancaps.net/tv/episodeimages.php"
            "?22491-Rick_and_Morty_Season_2/Episode_1"
        ),
        ("https://fancaps.net/tv/episodeimages.php?22491-"),
        ("https://fancaps.net/tv/episodeimages.php?22491"),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        groups = match.groups()
        self.episode_url = self.root + id_groups_to_str(groups)
        self.episode_id = groups[0]
        self._base_original = "https://cdni.fancaps.net/file/fancaps-tvimages/"
        self._base_fallback = (
            "https://tvcdn.fancaps.net/",
            "https://tvthumbs.fancaps.net/",
        )

    def metadata(self, page):
        series_match = re.search(
            rf"<a href=\"/tv/showimages\.php\?{ID_PATTERN}\">", page
        )
        return {
            "episode_id": self.episode_id,
            **extract_episode(page),
            "series": text.split_html(
                text.extr(page, series_match[0], "</a>")
            )[0],
            "series_url": (
                "https://fancaps.net/tv/episodeimages.php",
                f"?{id_groups_to_str(series_match.groups())}"
            )
        }

    def _image_fallback(self, filename):
        for base_url in self._base_fallback:
            yield base_url + filename

    def items(self):
        true_episode_url = self.request(
            text.ensure_http_scheme(self.episode_url)
        ).url
        page_idx = 1
        metadata = None
        while True:
            page = self.request(f"{true_episode_url}&page={page_idx}").text
            if metadata is None:
                metadata = self.metadata(page)

            image_ids_gen = text.extract_iter(
                page,
                '<a href="picture.php?/',
                '"'
            )

            # First 4 images are top images of an episode
            for _ in range(SKIP_FIRST_N_IMAGES):
                next(image_ids_gen, None)

            is_last_page = True
            for image_id in image_ids_gen:
                is_last_page = False
                yield Message.Directory, metadata
                filename = f"{image_id}.jpg"
                yield Message.Url, self._base_original + filename, {
                    "_fallback": self._image_fallback(filename),
                    "image_id": image_id,
                    "extension": "jpg",
                }

            if is_last_page:
                break
            page_idx += 1


class FancapsTvSeriesExtractor(Extractor):
    """Extractor for a TV series on fancaps.net"""

    category = "fancaps"
    subcategory = "tv-series"
    root = "https://fancaps.net/tv/showimages.php?"
    pattern = TV_BASE_PATTERN + rf"showimages\.php\?{ID_PATTERN}"
    test = ((
        "https://fancaps.net/tv/showimages.php"
        "?22490-Rick_and_Morty_Season_2"
    ),)

    def __init__(self, match):
        Extractor.__init__(self, match)
        groups = match.groups()
        self.series_url = self.root + id_groups_to_str(groups)
        self.series_id = groups[0]

    def items(self):
        true_series_url = self.request(
            text.ensure_http_scheme(self.series_url)
        ).url
        page_idx = 1
        while True:
            page = self.request(f"{true_series_url}&page={page_idx}").text
            for a_html in text.extract_iter(
                page, '<h3 style="font-size:21px;">', "</h3>"
            ):
                episode_id = id_groups_to_str(
                    re.search(
                        rf"/tv/episodeimages\.php\?{ID_PATTERN}",
                        a_html
                    ).groups()
                )
                yield Message.Queue, (
                    "https://fancaps.net/tv/episodeimages.php"
                    f"?{episode_id}"
                ), {
                    "_extractor": FancapsTvEpisodeExtractor
                }

            if re.search('<a href="#">Next', page) is not None:
                break

            page_idx += 1


class FancapsMovieExtractor(Extractor):
    """Extractor for a movie on fancaps.net"""

    category = "fancaps"
    subcategory = "movie"
    directory_fmt = ("{category}", "{movie_id} {movie}")
    filename_fmt = "{image_id}.{extension}"
    archive_fmt = "{movie_id}"
    root = "https://fancaps.net/movies/MovieImages.php?movieid="
    pattern = MOVIE_BASE_PATTERN + r"MovieImages\.php\?(?:.*&)?movieid=(\d+)"
    test = (
        ("https://fancaps.net/movies/MovieImages.php?movieid=4156&page=1"),
        (
            "https://fancaps.net/movies/MovieImages.php"
            "?name=Elemental_2023&movieid=4156&page=2"
        ),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.movie_id = match.group(1)
        self.movie_url = self.root + self.movie_id
        self._base_original = "https://cdni.fancaps.net/file/" \
            "fancaps-movieimages/"
        self._base_fallback = (
            "https://mvcdn.fancaps.net/",
            "https://moviethumbs.fancaps.net/",
        )

    def metadata(self, page):
        return {
            "movie_id": self.movie_id,
            "movie": text.extr(page, '<h2 class="post_title ">', "</h2>")
            .strip()
            .replace("Images from ", ""),
        }

    def _image_fallback(self, filename):
        for base_url in self._base_fallback:
            yield base_url + filename

    def items(self):
        page_idx = 1
        metadata = None
        while True:
            page = self.request(f"{self.movie_url}&page={page_idx}").text
            if metadata is None:
                metadata = self.metadata(page)

            image_ids_gen = text.extract_iter(
                page,
                '<a href="Image.php?imageid=', '"'
            )

            is_last_page = True
            for image_id in image_ids_gen:
                is_last_page = False
                yield Message.Directory, metadata
                filename = f"{image_id}.jpg"
                yield Message.Url, self._base_original + filename, {
                    "_fallback": self._image_fallback(filename),
                    "image_id": image_id,
                    "extension": "jpg",
                }

            if is_last_page:
                break
            page_idx += 1
