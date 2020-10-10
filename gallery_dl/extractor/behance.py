# -*- coding: utf-8 -*-

# Copyright 2018-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.behance.net/"""

from .common import Extractor, Message
from .. import text
import json


class BehanceExtractor(Extractor):
    """Base class for behance extractors"""
    category = "behance"
    root = "https://www.behance.net"

    def items(self):
        yield Message.Version, 1
        for gallery in self.galleries():
            gallery["_extractor"] = BehanceGalleryExtractor
            yield Message.Queue, gallery["url"], self._update(gallery)

    def galleries(self):
        """Return all relevant gallery URLs"""

    @staticmethod
    def _update(data):
        # compress data to simple lists
        if data["fields"] and isinstance(data["fields"][0], dict):
            data["fields"] = [
                field.get("name") or field.get("label")
                for field in data["fields"]
            ]
        data["owners"] = [
            owner.get("display_name") or owner.get("displayName")
            for owner in data["owners"]
        ]

        tags = data.get("tags") or ()
        if tags and isinstance(tags[0], dict):
            tags = [tag["title"] for tag in tags]
        data["tags"] = tags

        # backwards compatibility
        data["gallery_id"] = data["id"]
        data["title"] = data["name"]
        data["user"] = ", ".join(data["owners"])

        return data


class BehanceGalleryExtractor(BehanceExtractor):
    """Extractor for image galleries from www.behance.net"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{owners:J, }", "{id} {name}")
    filename_fmt = "{category}_{id}_{num:>02}.{extension}"
    archive_fmt = "{id}_{num}"
    pattern = r"(?:https?://)?(?:www\.)?behance\.net/gallery/(\d+)"
    test = (
        ("https://www.behance.net/gallery/17386197/A-Short-Story", {
            "count": 2,
            "url": "ab79bd3bef8d3ae48e6ac74fd995c1dfaec1b7d2",
            "keyword": {
                "id": 17386197,
                "name": 're:"Hi". A short story about the important things ',
                "owners": ["Place Studio", "Julio César Velazquez"],
                "fields": ["Animation", "Character Design", "Directing"],
                "tags": list,
                "module": dict,
            },
        }),
        ("https://www.behance.net/gallery/21324767/Nevada-City", {
            "count": 6,
            "url": "0258fe194fe7d828d6f2c7f6086a9a0a4140db1d",
            "keyword": {"owners": ["Alex Strohl"]},
        }),
        # 'media_collection' modules
        ("https://www.behance.net/gallery/88276087/Audi-R8-RWD", {
            "count": 20,
            "url": "6bebff0d37f85349f9ad28bd8b76fd66627c1e2f",
        }),
    )

    def __init__(self, match):
        BehanceExtractor.__init__(self, match)
        self.gallery_id = match.group(1)

    def items(self):
        data = self.get_gallery_data()
        imgs = self.get_images(data)
        data["count"] = len(imgs)

        yield Message.Version, 1
        yield Message.Directory, data
        for data["num"], (url, module) in enumerate(imgs, 1):
            data["module"] = module
            data["extension"] = text.ext_from_url(url)
            yield Message.Url, url, data

    def get_gallery_data(self):
        """Collect gallery info dict"""
        url = "{}/gallery/{}/a".format(self.root, self.gallery_id)
        cookies = {
            "_evidon_consent_cookie":
                '{"consent_date":"2019-01-31T09:41:15.132Z"}',
            "bcp": "4c34489d-914c-46cd-b44c-dfd0e661136d",
            "gk_suid": "66981391",
            "gki": '{"feature_project_view":false,'
                   '"feature_discover_login_prompt":false,'
                   '"feature_project_login_prompt":false}',
            "ilo0": "true",
        }
        page = self.request(url, cookies=cookies).text

        data = json.loads(text.extract(
            page, 'id="beconfig-store_state">', '</script>')[0])
        return self._update(data["project"]["project"])

    @staticmethod
    def get_images(data):
        """Extract image results from an API response"""
        result = []
        append = result.append

        for module in data["modules"]:
            mtype = module["type"]

            if mtype == "image":
                url = module["sizes"]["original"]
                append((url, module))

            elif mtype == "media_collection":
                for component in module["components"]:
                    url = component["sizes"]["source"]
                    append((url, module))

            elif mtype == "embed":
                embed = module.get("original_embed") or module.get("embed")
                if embed:
                    url = "ytdl:" + text.extract(embed, 'src="', '"')[0]
                    append((url, module))

        return result


class BehanceUserExtractor(BehanceExtractor):
    """Extractor for a user's galleries from www.behance.net"""
    subcategory = "user"
    categorytransfer = True
    pattern = r"(?:https?://)?(?:www\.)?behance\.net/([^/?&#]+)/?$"
    test = ("https://www.behance.net/alexstrohl", {
        "count": ">= 8",
        "pattern": BehanceGalleryExtractor.pattern,
    })

    def __init__(self, match):
        BehanceExtractor.__init__(self, match)
        self.user = match.group(1)

    def galleries(self):
        url = "{}/{}/projects".format(self.root, self.user)
        params = {"offset": 0}
        headers = {"X-Requested-With": "XMLHttpRequest"}

        while True:
            data = self.request(url, params=params, headers=headers).json()
            work = data["profile"]["activeSection"]["work"]
            yield from work["projects"]
            if not work["hasMore"]:
                return
            params["offset"] += len(work["projects"])


class BehanceCollectionExtractor(BehanceExtractor):
    """Extractor for a collection's galleries from www.behance.net"""
    subcategory = "collection"
    categorytransfer = True
    pattern = r"(?:https?://)?(?:www\.)?behance\.net/collection/(\d+)"
    test = ("https://www.behance.net/collection/71340149/inspiration", {
        "count": ">= 145",
        "pattern": BehanceGalleryExtractor.pattern,
    })

    def __init__(self, match):
        BehanceExtractor.__init__(self, match)
        self.collection_id = match.group(1)

    def galleries(self):
        url = self.root + "/v3/graphql"
        headers = {
            "Origin" : self.root,
            "Referer": self.root + "/collection/" + self.collection_id,
            "X-BCP"           : "4c34489d-914c-46cd-b44c-dfd0e661136d",
            "X-NewRelic-ID"   : "VgUFVldbGwsFU1BRDwUBVw==",
            "X-Requested-With": "XMLHttpRequest",
        }
        cookies = {
            "bcp"    : "4c34489d-914c-46cd-b44c-dfd0e661136d",
            "gk_suid": "66981391",
            "ilo0"   : "true",
        }

        query = """
query GetMoodboardItemsAndRecommendations(
    $id: Int!
    $firstItem: Int!
    $afterItem: String
    $shouldGetRecommendations: Boolean!
    $shouldGetItems: Boolean!
    $shouldGetMoodboardFields: Boolean!
  ) {
    viewer @include(if: $shouldGetMoodboardFields) {
      isOptedOutOfRecommendations
    }
    moodboard(id: $id) {
      ...moodboardFields @include(if: $shouldGetMoodboardFields)

      items(first: $firstItem, after: $afterItem) @include(if: $shouldGetItems)
      {
        pageInfo {
          endCursor
          hasNextPage
        }
        nodes {
          ...nodesFields
        }
      }

      recommendedItems(first: 80) @include(if: $shouldGetRecommendations) {
        nodes {
          ...nodesFields
          fetchSource
        }
      }
    }
  }

  fragment moodboardFields on Moodboard {
    id
    label
    privacy
    followerCount
    isFollowing
    projectCount
    url
    isOwner
    owners {
      id
      displayName
      url
      firstName
      location
      locationUrl
      images {
        size_50 {
          url
        }
        size_100 {
          url
        }
        size_115 {
          url
        }
        size_230 {
          url
        }
        size_138 {
          url
        }
        size_276 {
          url
        }
      }
    }
  }

  fragment projectFields on Project {
    id
    isOwner
    publishedOn
    matureAccess
    hasMatureContent
    modifiedOn
    name
    url
    isPrivate
    slug
    fields {
      label
    }
    colors {
      r
      g
      b
    }
    owners {
      url
      displayName
      id
      location
      locationUrl
      isProfileOwner
      images {
        size_50 {
          url
        }
        size_100 {
          url
        }
        size_115 {
          url
        }
        size_230 {
          url
        }
        size_138 {
          url
        }
        size_276 {
          url
        }
      }
    }
    covers {
      size_original {
        url
      }
      size_max_808 {
        url
      }
      size_808 {
        url
      }
      size_404 {
        url
      }
      size_202 {
        url
      }
      size_230 {
        url
      }
      size_115 {
        url
      }
    }
    stats {
      views {
        all
      }
      appreciations {
        all
      }
      comments {
        all
      }
    }
  }

  fragment exifDataValueFields on exifDataValue {
    id
    label
    value
    searchValue
  }

  fragment nodesFields on MoodboardItem {
    id
    entityType
    width
    height
    flexWidth
    flexHeight
    images {
      size
      url
    }

    entity {
      ... on Project {
        ...projectFields
      }

      ... on ImageModule {
        project {
          ...projectFields
        }

        exifData {
          lens {
            ...exifDataValueFields
          }
          software {
            ...exifDataValueFields
          }
          makeAndModel {
            ...exifDataValueFields
          }
          focalLength {
            ...exifDataValueFields
          }
          iso {
            ...exifDataValueFields
          }
          location {
            ...exifDataValueFields
          }
          flash {
            ...exifDataValueFields
          }
          exposureMode {
            ...exifDataValueFields
          }
          shutterSpeed {
            ...exifDataValueFields
          }
          aperture {
            ...exifDataValueFields
          }
        }
      }

      ... on MediaCollectionComponent {
        project {
          ...projectFields
        }
      }
    }
  }
"""
        variables = {
            "afterItem": "MAo=",
            "firstItem": 40,
            "id"       : self.collection_id,
            "shouldGetItems"          : True,
            "shouldGetMoodboardFields": False,
            "shouldGetRecommendations": False,
        }
        data = {"query": query, "variables": variables}

        while True:
            items = self.request(
                url, method="POST", headers=headers,
                cookies=cookies, json=data,
            ).json()["data"]["moodboard"]["items"]

            for node in items["nodes"]:
                yield node["entity"]

            if not items["pageInfo"]["hasNextPage"]:
                return
            variables["afterItem"] = items["pageInfo"]["endCursor"]
