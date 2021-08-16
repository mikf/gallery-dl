# -*- coding: utf-8 -*-

# Copyright 2019-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://500px.com/"""

from .common import Extractor, Message
import json

BASE_PATTERN = r"(?:https?://)?(?:web\.)?500px\.com"


class _500pxExtractor(Extractor):
    """Base class for 500px extractors"""
    category = "500px"
    directory_fmt = ("{category}", "{user[username]}")
    filename_fmt = "{id}_{name}.{extension}"
    archive_fmt = "{id}"
    root = "https://500px.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.session.headers["Referer"] = self.root + "/"

    def items(self):
        first = True
        data = self.metadata()

        for photo in self.photos():
            url = photo["images"][-1]["url"]
            photo["extension"] = photo["image_format"]
            if data:
                photo.update(data)
            if first:
                first = False
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

    def _request_api(self, url, params, csrf_token=None):
        headers = {"Origin": self.root, "X-CSRF-Token": csrf_token}
        return self.request(url, headers=headers, params=params).json()

    def _request_graphql(self, opname, variables):
        url = "https://api.500px.com/graphql"
        data = {
            "operationName": opname,
            "variables"    : json.dumps(variables),
            "query"        : QUERIES[opname],
        }
        return self.request(url, method="POST", json=data).json()["data"]


class _500pxUserExtractor(_500pxExtractor):
    """Extractor for photos from a user's photostream on 500px.com"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/(?!photo/)(?:p/)?([^/?#]+)/?(?:$|[?#])"
    test = (
        ("https://500px.com/p/light_expression_photography", {
            "pattern": r"https?://drscdn.500px.org/photo/\d+/m%3D4096/v2",
            "range": "1-99",
            "count": 99,
        }),
        ("https://500px.com/light_expression_photography"),
        ("https://web.500px.com/light_expression_photography"),
    )

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
    test = (
        ("https://500px.com/p/fashvamp/galleries/lera", {
            "url": "002dc81dee5b4a655f0e31ad8349e8903b296df6",
            "count": 3,
            "keyword": {
                "gallery": dict,
                "user": dict,
            },
        }),
        # unavailable photos (#1335)
        ("https://500px.com/p/Light_Expression_Photography/galleries/street", {
            "count": 4,
        }),
        ("https://500px.com/fashvamp/galleries/lera"),
    )

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


class _500pxImageExtractor(_500pxExtractor):
    """Extractor for individual images from 500px.com"""
    subcategory = "image"
    pattern = BASE_PATTERN + r"/photo/(\d+)"
    test = ("https://500px.com/photo/222049255/queen-of-coasts", {
        "url": "fbdf7df39325cae02f5688e9f92935b0e7113315",
        "count": 1,
        "keyword": {
            "camera": "Canon EOS 600D",
            "camera_info": dict,
            "comments": list,
            "comments_count": int,
            "created_at": "2017-08-01T08:40:05+00:00",
            "description": str,
            "editored_by": None,
            "editors_choice": False,
            "extension": "jpg",
            "feature": "popular",
            "feature_date": "2017-08-01T09:58:28+00:00",
            "focal_length": "208",
            "height": 3111,
            "id": 222049255,
            "image_format": "jpg",
            "image_url": list,
            "images": list,
            "iso": "100",
            "lens": "EF-S55-250mm f/4-5.6 IS II",
            "lens_info": dict,
            "liked": None,
            "location": None,
            "location_details": dict,
            "name": "Queen Of Coasts",
            "nsfw": False,
            "privacy": False,
            "profile": True,
            "rating": float,
            "status": 1,
            "tags": list,
            "taken_at": "2017-05-04T17:36:51+00:00",
            "times_viewed": int,
            "url": "/photo/222049255/Queen-Of-Coasts-by-Olesya-Nabieva",
            "user": dict,
            "user_id": 12847235,
            "votes_count": int,
            "watermark": True,
            "width": 4637,
        },
    })

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

}
