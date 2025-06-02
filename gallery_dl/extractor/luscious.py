# -*- coding: utf-8 -*-

# Copyright 2016-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://members.luscious.net/"""

from .common import Extractor, Message
from .. import text, exception


class LusciousExtractor(Extractor):
    """Base class for luscious extractors"""
    category = "luscious"
    cookies_domain = ".luscious.net"
    root = "https://members.luscious.net"

    def _graphql(self, op, variables, query):
        data = {
            "id"           : 1,
            "operationName": op,
            "query"        : query,
            "variables"    : variables,
        }
        response = self.request(
            "{}/graphql/nobatch/?operationName={}".format(self.root, op),
            method="POST", json=data, fatal=False,
        )

        if response.status_code >= 400:
            self.log.debug("Server response: %s", response.text)
            raise exception.StopExtraction(
                "GraphQL query failed ('%s %s')",
                response.status_code, response.reason)

        return response.json()["data"]


class LusciousAlbumExtractor(LusciousExtractor):
    """Extractor for image albums from luscious.net"""
    subcategory = "album"
    filename_fmt = "{category}_{album[id]}_{num:>03}.{extension}"
    directory_fmt = ("{category}", "{album[id]} {album[title]}")
    archive_fmt = "{album[id]}_{id}"
    pattern = (r"(?:https?://)?(?:www\.|members\.)?luscious\.net"
               r"/(?:albums|pictures/c/[^/?#]+/album)/[^/?#]+_(\d+)")
    example = "https://luscious.net/albums/TITLE_12345/"

    def __init__(self, match):
        LusciousExtractor.__init__(self, match)
        self.album_id = match.group(1)

    def _init(self):
        self.gif = self.config("gif", False)

    def items(self):
        album = self.metadata()
        yield Message.Directory, {"album": album}
        for num, image in enumerate(self.images(), 1):
            image["num"] = num
            image["album"] = album

            try:
                image["thumbnail"] = image.pop("thumbnails")[0]["url"]
            except LookupError:
                image["thumbnail"] = ""

            image["tags"] = [item["text"] for item in image["tags"]]
            image["date"] = text.parse_timestamp(image["created"])
            image["id"] = text.parse_int(image["id"])

            url = (image["url_to_original"] or image["url_to_video"]
                   if self.gif else
                   image["url_to_video"] or image["url_to_original"])

            yield Message.Url, url, text.nameext_from_url(url, image)

    def metadata(self):
        variables = {
            "id": self.album_id,
        }

        query = """
query AlbumGet($id: ID!) {
    album {
        get(id: $id) {
            ... on Album {
                ...AlbumStandard
            }
            ... on MutationError {
                errors {
                    code
                    message
                }
            }
        }
    }
}

fragment AlbumStandard on Album {
    __typename
    id
    title
    labels
    description
    created
    modified
    like_status
    number_of_favorites
    rating
    status
    marked_for_deletion
    marked_for_processing
    number_of_pictures
    number_of_animated_pictures
    slug
    is_manga
    url
    download_url
    permissions
    cover {
        width
        height
        size
        url
    }
    created_by {
        id
        name
        display_name
        user_title
        avatar {
            url
            size
        }
        url
    }
    content {
        id
        title
        url
    }
    language {
        id
        title
        url
    }
    tags {
        id
        category
        text
        url
        count
    }
    genres {
        id
        title
        slug
        url
    }
    audiences {
        id
        title
        url
        url
    }
    last_viewed_picture {
        id
        position
        url
    }
}
"""
        album = self._graphql("AlbumGet", variables, query)["album"]["get"]
        if "errors" in album:
            raise exception.NotFoundError("album")

        album["audiences"] = [item["title"] for item in album["audiences"]]
        album["genres"] = [item["title"] for item in album["genres"]]
        album["tags"] = [item["text"] for item in album["tags"]]

        album["cover"] = album["cover"]["url"]
        album["content"] = album["content"]["title"]
        album["language"] = album["language"]["title"].partition(" ")[0]
        album["created_by"] = album["created_by"]["display_name"]

        album["id"] = text.parse_int(album["id"])
        album["date"] = text.parse_timestamp(album["created"])

        return album

    def images(self):
        variables = {
            "input": {
                "filters": [{
                    "name" : "album_id",
                    "value": self.album_id,
                }],
                "display": "position",
                "page"   : 1,
            },
        }

        query = """
query AlbumListOwnPictures($input: PictureListInput!) {
    picture {
        list(input: $input) {
            info {
                ...FacetCollectionInfo
            }
            items {
                ...PictureStandardWithoutAlbum
            }
        }
    }
}

fragment FacetCollectionInfo on FacetCollectionInfo {
    page
    has_next_page
    has_previous_page
    total_items
    total_pages
    items_per_page
    url_complete
    url_filters_only
}

fragment PictureStandardWithoutAlbum on Picture {
    __typename
    id
    title
    created
    like_status
    number_of_comments
    number_of_favorites
    status
    width
    height
    resolution
    aspect_ratio
    url_to_original
    url_to_video
    is_animated
    position
    tags {
        id
        category
        text
        url
    }
    permissions
    url
    thumbnails {
        width
        height
        size
        url
    }
}
"""
        while True:
            data = self._graphql("AlbumListOwnPictures", variables, query)
            yield from data["picture"]["list"]["items"]

            if not data["picture"]["list"]["info"]["has_next_page"]:
                return
            variables["input"]["page"] += 1


class LusciousSearchExtractor(LusciousExtractor):
    """Extractor for album searches on luscious.net"""
    subcategory = "search"
    pattern = (r"(?:https?://)?(?:www\.|members\.)?luscious\.net"
               r"/albums/list/?(?:\?([^#]+))?")
    example = "https://luscious.net/albums/list/?tagged=TAG"

    def __init__(self, match):
        LusciousExtractor.__init__(self, match)
        self.query = match.group(1)

    def items(self):
        query = text.parse_query(self.query)
        display = query.pop("display", "date_newest")
        page = query.pop("page", None)

        variables = {
            "input": {
                "display": display,
                "filters": [{"name": n, "value": v} for n, v in query.items()],
                "page": text.parse_int(page, 1),
            },
        }

        query = """
query AlbumListWithPeek($input: AlbumListInput!) {
    album {
        list(input: $input) {
            info {
                ...FacetCollectionInfo
            }
            items {
                ...AlbumMinimal
                peek_thumbnails {
                    width
                    height
                    size
                    url
                }
            }
        }
    }
}

fragment FacetCollectionInfo on FacetCollectionInfo {
    page
    has_next_page
    has_previous_page
    total_items
    total_pages
    items_per_page
    url_complete
    url_filters_only
}

fragment AlbumMinimal on Album {
    __typename
    id
    title
    labels
    description
    created
    modified
    number_of_favorites
    number_of_pictures
    slug
    is_manga
    url
    download_url
    cover {
        width
        height
        size
        url
    }
    content {
        id
        title
        url
    }
    language {
        id
        title
        url
    }
    tags {
        id
        category
        text
        url
        count
    }
    genres {
        id
        title
        slug
        url
    }
    audiences {
        id
        title
        url
    }
}
"""
        while True:
            data = self._graphql("AlbumListWithPeek", variables, query)

            for album in data["album"]["list"]["items"]:
                album["url"] = self.root + album["url"]
                album["_extractor"] = LusciousAlbumExtractor
                yield Message.Queue, album["url"], album

            if not data["album"]["list"]["info"]["has_next_page"]:
                return
            variables["input"]["page"] += 1
