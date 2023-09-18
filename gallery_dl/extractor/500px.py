# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://500px.com/"""

from .common import Extractor, Message
from .. import util

BASE_PATTERN = r"(?:https?://)?(?:web\.)?500px\.com"


class _500pxExtractor(Extractor):
    """Base class for 500px extractors"""
    category = "500px"
    directory_fmt = ("{category}", "{user[username]}")
    filename_fmt = "{id}_{name}.{extension}"
    archive_fmt = "{id}"
    root = "https://500px.com"
    cookies_domain = ".500px.com"

    def items(self):
        data = self.metadata()

        for photo in self.photos():
            url = photo["images"][-1]["url"]
            photo["extension"] = photo["image_format"]
            if data:
                photo.update(data)
            yield Message.Directory, photo
            yield Message.Url, url, photo

    def metadata(self):
        """Returns general metadata"""

    def photos(self):
        """Returns an iterable containing all relevant photo IDs"""

    def _extend(self, edges):
        """Extend photos with additional metadata and higher resolution URLs"""
        ids = [str(edge["node"]["legacyId"]) for edge in edges]

        url = "https://api.500px.com/v1/photos"
        params = {
            "expanded_user_info"    : "true",
            "include_tags"          : "true",
            "include_geo"           : "true",
            "include_equipment_info": "true",
            "vendor_photos"         : "true",
            "include_licensing"     : "true",
            "include_releases"      : "true",
            "liked_by"              : "1",
            "following_sample"      : "100",
            "image_size"            : "4096",
            "ids"                   : ",".join(ids),
        }

        photos = self._request_api(url, params)["photos"]
        return [
            photos[pid] for pid in ids
            if pid in photos or
            self.log.warning("Unable to fetch photo %s", pid)
        ]

    def _request_api(self, url, params):
        headers = {
            "Origin": self.root,
            "x-csrf-token": self.cookies.get(
                "x-csrf-token", domain=".500px.com"),
        }
        return self.request(url, headers=headers, params=params).json()

    def _request_graphql(self, opname, variables):
        url = "https://api.500px.com/graphql"
        headers = {
            "x-csrf-token": self.cookies.get(
                "x-csrf-token", domain=".500px.com"),
        }
        data = {
            "operationName": opname,
            "variables"    : util.json_dumps(variables),
            "query"        : QUERIES[opname],
        }
        return self.request(
            url, method="POST", headers=headers, json=data).json()["data"]


class _500pxUserExtractor(_500pxExtractor):
    """Extractor for photos from a user's photostream on 500px.com"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/(?!photo/|liked)(?:p/)?([^/?#]+)/?(?:$|[?#])"
    example = "https://500px.com/USER"

    def __init__(self, match):
        _500pxExtractor.__init__(self, match)
        self.user = match.group(1)

    def photos(self):
        variables = {"username": self.user, "pageSize": 20}
        photos = self._request_graphql(
            "OtherPhotosQuery", variables,
        )["user"]["photos"]

        while True:
            yield from self._extend(photos["edges"])

            if not photos["pageInfo"]["hasNextPage"]:
                return

            variables["cursor"] = photos["pageInfo"]["endCursor"]
            photos = self._request_graphql(
                "OtherPhotosPaginationContainerQuery", variables,
            )["userByUsername"]["photos"]


class _500pxGalleryExtractor(_500pxExtractor):
    """Extractor for photo galleries on 500px.com"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{user[username]}", "{gallery[name]}")
    pattern = (BASE_PATTERN + r"/(?!photo/)(?:p/)?"
               r"([^/?#]+)/galleries/([^/?#]+)")
    example = "https://500px.com/USER/galleries/GALLERY"

    def __init__(self, match):
        _500pxExtractor.__init__(self, match)
        self.user_name, self.gallery_name = match.groups()
        self.user_id = self._photos = None

    def metadata(self):
        user = self._request_graphql(
            "ProfileRendererQuery", {"username": self.user_name},
        )["profile"]
        self.user_id = str(user["legacyId"])

        variables = {
            "galleryOwnerLegacyId": self.user_id,
            "ownerLegacyId"       : self.user_id,
            "slug"                : self.gallery_name,
            "token"               : None,
            "pageSize"            : 20,
        }
        gallery = self._request_graphql(
            "GalleriesDetailQueryRendererQuery", variables,
        )["gallery"]

        self._photos = gallery["photos"]
        del gallery["photos"]
        return {
            "gallery": gallery,
            "user"   : user,
        }

    def photos(self):
        photos = self._photos
        variables = {
            "ownerLegacyId": self.user_id,
            "slug"         : self.gallery_name,
            "token"        : None,
            "pageSize"     : 20,
        }

        while True:
            yield from self._extend(photos["edges"])

            if not photos["pageInfo"]["hasNextPage"]:
                return

            variables["cursor"] = photos["pageInfo"]["endCursor"]
            photos = self._request_graphql(
                "GalleriesDetailPaginationContainerQuery", variables,
            )["galleryByOwnerIdAndSlugOrToken"]["photos"]


class _500pxFavoriteExtractor(_500pxExtractor):
    """Extractor for favorite 500px photos"""
    subcategory = "favorite"
    pattern = BASE_PATTERN + r"/liked/?$"
    example = "https://500px.com/liked"

    def photos(self):
        variables = {"pageSize": 20}
        photos = self._request_graphql(
            "LikedPhotosQueryRendererQuery", variables,
        )["likedPhotos"]

        while True:
            yield from self._extend(photos["edges"])

            if not photos["pageInfo"]["hasNextPage"]:
                return

            variables["cursor"] = photos["pageInfo"]["endCursor"]
            photos = self._request_graphql(
                "LikedPhotosPaginationContainerQuery", variables,
            )["likedPhotos"]


class _500pxImageExtractor(_500pxExtractor):
    """Extractor for individual images from 500px.com"""
    subcategory = "image"
    pattern = BASE_PATTERN + r"/photo/(\d+)"
    example = "https://500px.com/photo/12345/TITLE"

    def __init__(self, match):
        _500pxExtractor.__init__(self, match)
        self.photo_id = match.group(1)

    def photos(self):
        edges = ({"node": {"legacyId": self.photo_id}},)
        return self._extend(edges)


QUERIES = {

    "OtherPhotosQuery": """\
query OtherPhotosQuery($username: String!, $pageSize: Int) {
  user: userByUsername(username: $username) {
    ...OtherPhotosPaginationContainer_user_RlXb8
    id
  }
}

fragment OtherPhotosPaginationContainer_user_RlXb8 on User {
  photos(first: $pageSize, privacy: PROFILE, sort: ID_DESC) {
    edges {
      node {
        id
        legacyId
        canonicalPath
        width
        height
        name
        isLikedByMe
        notSafeForWork
        photographer: uploader {
          id
          legacyId
          username
          displayName
          canonicalPath
          followedByUsers {
            isFollowedByMe
          }
        }
        images(sizes: [33, 35]) {
          size
          url
          jpegUrl
          webpUrl
          id
        }
        __typename
      }
      cursor
    }
    totalCount
    pageInfo {
      endCursor
      hasNextPage
    }
  }
}
""",

    "OtherPhotosPaginationContainerQuery": """\
query OtherPhotosPaginationContainerQuery($username: String!, $pageSize: Int, $cursor: String) {
  userByUsername(username: $username) {
    ...OtherPhotosPaginationContainer_user_3e6UuE
    id
  }
}

fragment OtherPhotosPaginationContainer_user_3e6UuE on User {
  photos(first: $pageSize, after: $cursor, privacy: PROFILE, sort: ID_DESC) {
    edges {
      node {
        id
        legacyId
        canonicalPath
        width
        height
        name
        isLikedByMe
        notSafeForWork
        photographer: uploader {
          id
          legacyId
          username
          displayName
          canonicalPath
          followedByUsers {
            isFollowedByMe
          }
        }
        images(sizes: [33, 35]) {
          size
          url
          jpegUrl
          webpUrl
          id
        }
        __typename
      }
      cursor
    }
    totalCount
    pageInfo {
      endCursor
      hasNextPage
    }
  }
}
""",

    "ProfileRendererQuery": """\
query ProfileRendererQuery($username: String!) {
  profile: userByUsername(username: $username) {
    id
    legacyId
    userType: type
    username
    firstName
    displayName
    registeredAt
    canonicalPath
    avatar {
      ...ProfileAvatar_avatar
      id
    }
    userProfile {
      firstname
      lastname
      state
      country
      city
      about
      id
    }
    socialMedia {
      website
      twitter
      instagram
      facebook
      id
    }
    coverPhotoUrl
    followedByUsers {
      totalCount
      isFollowedByMe
    }
    followingUsers {
      totalCount
    }
    membership {
      expiryDate
      membershipTier: tier
      photoUploadQuota
      refreshPhotoUploadQuotaAt
      paymentStatus
      id
    }
    profileTabs {
      tabs {
        name
        visible
      }
    }
    ...EditCover_cover
    photoStats {
      likeCount
      viewCount
    }
    photos(privacy: PROFILE) {
      totalCount
    }
    licensingPhotos(status: ACCEPTED) {
      totalCount
    }
    portfolio {
      id
      status
      userDisabled
    }
  }
}

fragment EditCover_cover on User {
  coverPhotoUrl
}

fragment ProfileAvatar_avatar on UserAvatar {
  images(sizes: [MEDIUM, LARGE]) {
    size
    url
    id
  }
}
""",

    "GalleriesDetailQueryRendererQuery": """\
query GalleriesDetailQueryRendererQuery($galleryOwnerLegacyId: ID!, $ownerLegacyId: String, $slug: String, $token: String, $pageSize: Int, $gallerySize: Int) {
  galleries(galleryOwnerLegacyId: $galleryOwnerLegacyId, first: $gallerySize) {
    edges {
      node {
        legacyId
        description
        name
        privacy
        canonicalPath
        notSafeForWork
        buttonName
        externalUrl
        cover {
          images(sizes: [35, 33]) {
            size
            webpUrl
            jpegUrl
            id
          }
          id
        }
        photos {
          totalCount
        }
        id
      }
    }
  }
  gallery: galleryByOwnerIdAndSlugOrToken(ownerLegacyId: $ownerLegacyId, slug: $slug, token: $token) {
    ...GalleriesDetailPaginationContainer_gallery_RlXb8
    id
  }
}

fragment GalleriesDetailPaginationContainer_gallery_RlXb8 on Gallery {
  id
  legacyId
  name
  privacy
  notSafeForWork
  ownPhotosOnly
  canonicalPath
  publicSlug
  lastPublishedAt
  photosAddedSinceLastPublished
  reportStatus
  creator {
    legacyId
    id
  }
  cover {
    images(sizes: [33, 32, 36, 2048]) {
      url
      size
      webpUrl
      id
    }
    id
  }
  description
  externalUrl
  buttonName
  photos(first: $pageSize) {
    totalCount
    edges {
      cursor
      node {
        id
        legacyId
        canonicalPath
        name
        description
        category
        uploadedAt
        location
        width
        height
        isLikedByMe
        photographer: uploader {
          id
          legacyId
          username
          displayName
          canonicalPath
          avatar {
            images(sizes: SMALL) {
              url
              id
            }
            id
          }
          followedByUsers {
            totalCount
            isFollowedByMe
          }
        }
        images(sizes: [33, 32]) {
          size
          url
          webpUrl
          id
        }
        __typename
      }
    }
    pageInfo {
      endCursor
      hasNextPage
    }
  }
}
""",

    "GalleriesDetailPaginationContainerQuery": """\
query GalleriesDetailPaginationContainerQuery($ownerLegacyId: String, $slug: String, $token: String, $pageSize: Int, $cursor: String) {
  galleryByOwnerIdAndSlugOrToken(ownerLegacyId: $ownerLegacyId, slug: $slug, token: $token) {
    ...GalleriesDetailPaginationContainer_gallery_3e6UuE
    id
  }
}

fragment GalleriesDetailPaginationContainer_gallery_3e6UuE on Gallery {
  id
  legacyId
  name
  privacy
  notSafeForWork
  ownPhotosOnly
  canonicalPath
  publicSlug
  lastPublishedAt
  photosAddedSinceLastPublished
  reportStatus
  creator {
    legacyId
    id
  }
  cover {
    images(sizes: [33, 32, 36, 2048]) {
      url
      size
      webpUrl
      id
    }
    id
  }
  description
  externalUrl
  buttonName
  photos(first: $pageSize, after: $cursor) {
    totalCount
    edges {
      cursor
      node {
        id
        legacyId
        canonicalPath
        name
        description
        category
        uploadedAt
        location
        width
        height
        isLikedByMe
        photographer: uploader {
          id
          legacyId
          username
          displayName
          canonicalPath
          avatar {
            images(sizes: SMALL) {
              url
              id
            }
            id
          }
          followedByUsers {
            totalCount
            isFollowedByMe
          }
        }
        images(sizes: [33, 32]) {
          size
          url
          webpUrl
          id
        }
        __typename
      }
    }
    pageInfo {
      endCursor
      hasNextPage
    }
  }
}
""",

    "LikedPhotosQueryRendererQuery": """\
query LikedPhotosQueryRendererQuery($pageSize: Int) {
  ...LikedPhotosPaginationContainer_query_RlXb8
}

fragment LikedPhotosPaginationContainer_query_RlXb8 on Query {
  likedPhotos(first: $pageSize) {
    edges {
      node {
        id
        legacyId
        canonicalPath
        name
        description
        category
        uploadedAt
        location
        width
        height
        isLikedByMe
        notSafeForWork
        tags
        photographer: uploader {
          id
          legacyId
          username
          displayName
          canonicalPath
          avatar {
            images {
              url
              id
            }
            id
          }
          followedByUsers {
            totalCount
            isFollowedByMe
          }
        }
        images(sizes: [33, 35]) {
          size
          url
          jpegUrl
          webpUrl
          id
        }
        __typename
      }
      cursor
    }
    pageInfo {
      endCursor
      hasNextPage
    }
  }
}
""",

    "LikedPhotosPaginationContainerQuery": """\
query LikedPhotosPaginationContainerQuery($cursor: String, $pageSize: Int) {
  ...LikedPhotosPaginationContainer_query_3e6UuE
}

fragment LikedPhotosPaginationContainer_query_3e6UuE on Query {
  likedPhotos(first: $pageSize, after: $cursor) {
    edges {
      node {
        id
        legacyId
        canonicalPath
        name
        description
        category
        uploadedAt
        location
        width
        height
        isLikedByMe
        notSafeForWork
        tags
        photographer: uploader {
          id
          legacyId
          username
          displayName
          canonicalPath
          avatar {
            images {
              url
              id
            }
            id
          }
          followedByUsers {
            totalCount
            isFollowedByMe
          }
        }
        images(sizes: [33, 35]) {
          size
          url
          jpegUrl
          webpUrl
          id
        }
        __typename
      }
      cursor
    }
    pageInfo {
      endCursor
      hasNextPage
    }
  }
}
""",

}
