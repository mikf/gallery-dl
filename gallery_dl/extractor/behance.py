# -*- coding: utf-8 -*-

# Copyright 2018-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.behance.net/"""

from .common import Extractor, Message
from .. import text, util, exception


class BehanceExtractor(Extractor):
    """Base class for behance extractors"""
    category = "behance"
    root = "https://www.behance.net"
    request_interval = (2.0, 4.0)

    def _init(self):
        self._bcp = self.cookies.get("bcp", domain="www.behance.net")
        if not self._bcp:
            self._bcp = "4c34489d-914c-46cd-b44c-dfd0e661136d"
            self.cookies.set("bcp", self._bcp, domain="www.behance.net")

    def items(self):
        for gallery in self.galleries():
            gallery["_extractor"] = BehanceGalleryExtractor
            yield Message.Queue, gallery["url"], self._update(gallery)

    def galleries(self):
        """Return all relevant gallery URLs"""

    def _request_graphql(self, endpoint, variables):
        url = self.root + "/v3/graphql"
        headers = {
            "Origin": self.root,
            "X-BCP" : self._bcp,
            "X-Requested-With": "XMLHttpRequest",
        }
        data = {
            "query"    : GRAPHQL_QUERIES[endpoint],
            "variables": variables,
        }

        return self.request(url, method="POST", headers=headers,
                            json=data).json()["data"]

    def _update(self, data):
        # compress data to simple lists
        if data.get("fields") and isinstance(data["fields"][0], dict):
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

        data["date"] = text.parse_timestamp(
            data.get("publishedOn") or data.get("conceived_on") or 0)

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
    example = "https://www.behance.net/gallery/12345/TITLE"

    def __init__(self, match):
        BehanceExtractor.__init__(self, match)
        self.gallery_id = match.group(1)

    def _init(self):
        BehanceExtractor._init(self)

        modules = self.config("modules")
        if modules:
            if isinstance(modules, str):
                modules = modules.split(",")
            self.modules = set(modules)
        else:
            self.modules = {"image", "video", "mediacollection", "embed"}

    def items(self):
        data = self.get_gallery_data()
        imgs = self.get_images(data)
        data["count"] = len(imgs)

        yield Message.Directory, data
        for data["num"], (url, module) in enumerate(imgs, 1):
            data["module"] = module
            data["extension"] = (module.get("extension") or
                                 text.ext_from_url(url))
            yield Message.Url, url, data

    def get_gallery_data(self):
        """Collect gallery info dict"""
        url = "{}/gallery/{}/a".format(self.root, self.gallery_id)
        cookies = {
            "gki": '{"feature_project_view":false,'
                   '"feature_discover_login_prompt":false,'
                   '"feature_project_login_prompt":false}',
            "ilo0": "true",
        }
        page = self.request(url, cookies=cookies).text

        data = util.json_loads(text.extr(
            page, 'id="beconfig-store_state">', '</script>'))
        return self._update(data["project"]["project"])

    def get_images(self, data):
        """Extract image results from an API response"""
        if not data["modules"]:
            access = data.get("matureAccess")
            if access == "logged-out":
                raise exception.AuthorizationError(
                    "Mature content galleries require logged-in cookies")
            if access == "restricted-safe":
                raise exception.AuthorizationError(
                    "Mature content blocked in account settings")
            if access and access != "allowed":
                raise exception.AuthorizationError()
            return ()

        result = []
        append = result.append

        for module in data["modules"]:
            mtype = module["__typename"][:-6].lower()

            if mtype not in self.modules:
                self.log.debug("Skipping '%s' module", mtype)
                continue

            if mtype == "image":
                sizes = {
                    size["url"].rsplit("/", 2)[1]: size
                    for size in module["imageSizes"]["allAvailable"]
                }
                size = (sizes.get("source") or
                        sizes.get("max_3840") or
                        sizes.get("fs") or
                        sizes.get("hd") or
                        sizes.get("disp"))
                append((size["url"], module))

            elif mtype == "video":
                try:
                    url = text.extr(module["embed"], 'src="', '"')
                    page = self.request(text.unescape(url)).text

                    url = text.extr(page, '<source src="', '"')
                    if text.ext_from_url(url) == "m3u8":
                        url = "ytdl:" + url
                        module["_ytdl_manifest"] = "hls"
                        module["extension"] = "mp4"
                    append((url, module))
                    continue
                except Exception as exc:
                    self.log.debug("%s: %s", exc.__class__.__name__, exc)

                try:
                    renditions = module["videoData"]["renditions"]
                except Exception:
                    self.log.warning("No download URLs for video %s",
                                     module.get("id") or "???")
                    continue

                try:
                    url = [
                        r["url"] for r in renditions
                        if text.ext_from_url(r["url"]) != "m3u8"
                    ][-1]
                except Exception as exc:
                    self.log.debug("%s: %s", exc.__class__.__name__, exc)
                    url = "ytdl:" + renditions[-1]["url"]

                append((url, module))

            elif mtype == "mediacollection":
                for component in module["components"]:
                    for size in component["imageSizes"].values():
                        if size:
                            parts = size["url"].split("/")
                            parts[4] = "source"
                            append(("/".join(parts), module))
                            break

            elif mtype == "embed":
                embed = module.get("originalEmbed") or module.get("fluidEmbed")
                if embed:
                    embed = text.unescape(text.extr(embed, 'src="', '"'))
                    module["extension"] = "mp4"
                    append(("ytdl:" + embed, module))

            elif mtype == "text":
                module["extension"] = "txt"
                append(("text:" + module["text"], module))

        return result


class BehanceUserExtractor(BehanceExtractor):
    """Extractor for a user's galleries from www.behance.net"""
    subcategory = "user"
    categorytransfer = True
    pattern = r"(?:https?://)?(?:www\.)?behance\.net/([^/?#]+)/?$"
    example = "https://www.behance.net/USER"

    def __init__(self, match):
        BehanceExtractor.__init__(self, match)
        self.user = match.group(1)

    def galleries(self):
        endpoint = "GetProfileProjects"
        variables = {
            "username": self.user,
            "after"   : "MAo=",  # "0" in base64
        }

        while True:
            data = self._request_graphql(endpoint, variables)
            items = data["user"]["profileProjects"]
            yield from items["nodes"]

            if not items["pageInfo"]["hasNextPage"]:
                return
            variables["after"] = items["pageInfo"]["endCursor"]


class BehanceCollectionExtractor(BehanceExtractor):
    """Extractor for a collection's galleries from www.behance.net"""
    subcategory = "collection"
    categorytransfer = True
    pattern = r"(?:https?://)?(?:www\.)?behance\.net/collection/(\d+)"
    example = "https://www.behance.net/collection/12345/TITLE"

    def __init__(self, match):
        BehanceExtractor.__init__(self, match)
        self.collection_id = match.group(1)

    def galleries(self):
        endpoint = "GetMoodboardItemsAndRecommendations"
        variables = {
            "afterItem": "MAo=",  # "0" in base64
            "firstItem": 40,
            "id"       : int(self.collection_id),
            "shouldGetItems"          : True,
            "shouldGetMoodboardFields": False,
            "shouldGetRecommendations": False,
        }

        while True:
            data = self._request_graphql(endpoint, variables)
            items = data["moodboard"]["items"]

            for node in items["nodes"]:
                yield node["entity"]

            if not items["pageInfo"]["hasNextPage"]:
                return
            variables["afterItem"] = items["pageInfo"]["endCursor"]


GRAPHQL_QUERIES = {
    "GetProfileProjects": """\
query GetProfileProjects($username: String, $after: String) {
  user(username: $username) {
    profileProjects(first: 12, after: $after) {
      pageInfo {
        endCursor
        hasNextPage
      }
      nodes {
        __typename
        adminFlags {
          mature_lock
          privacy_lock
          dmca_lock
          flagged_lock
          privacy_violation_lock
          trademark_lock
          spam_lock
          eu_ip_lock
        }
        colors {
          r
          g
          b
        }
        covers {
          size_202 {
            url
          }
          size_404 {
            url
          }
          size_808 {
            url
          }
        }
        features {
          url
          name
          featuredOn
          ribbon {
            image
            image2x
            image3x
          }
        }
        fields {
          id
          label
          slug
          url
        }
        hasMatureContent
        id
        isFeatured
        isHiddenFromWorkTab
        isMatureReviewSubmitted
        isOwner
        isFounder
        isPinnedToSubscriptionOverview
        isPrivate
        linkedAssets {
          ...sourceLinkFields
        }
        linkedAssetsCount
        sourceFiles {
          ...sourceFileFields
        }
        matureAccess
        modifiedOn
        name
        owners {
          ...OwnerFields
          images {
            size_50 {
              url
            }
          }
        }
        premium
        publishedOn
        stats {
          appreciations {
            all
          }
          views {
            all
          }
          comments {
            all
          }
        }
        slug
        tools {
          id
          title
          category
          categoryLabel
          categoryId
          approved
          url
          backgroundColor
        }
        url
      }
    }
  }
}

fragment sourceFileFields on SourceFile {
  __typename
  sourceFileId
  projectId
  userId
  title
  assetId
  renditionUrl
  mimeType
  size
  category
  licenseType
  unitAmount
  currency
  tier
  hidden
  extension
  hasUserPurchased
}

fragment sourceLinkFields on LinkedAsset {
  __typename
  name
  premium
  url
  category
  licenseType
}

fragment OwnerFields on User {
  displayName
  hasPremiumAccess
  id
  isFollowing
  isProfileOwner
  location
  locationUrl
  url
  username
  availabilityInfo {
    availabilityTimeline
    isAvailableFullTime
    isAvailableFreelance
  }
}
""",

    "GetMoodboardItemsAndRecommendations": """\
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
    isAdmin
  }
  moodboard(id: $id) {
    ...moodboardFields @include(if: $shouldGetMoodboardFields)

    items(first: $firstItem, after: $afterItem) @include(if: $shouldGetItems) {
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
    ...OwnerFields
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
  __typename
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
  license {
    license
    description
    id
    label
    url
    text
    images
  }
  fields {
    label
  }
  colors {
    r
    g
    b
  }
  owners {
    ...OwnerFields
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

      colors {
        r
        g
        b
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

fragment OwnerFields on User {
  displayName
  hasPremiumAccess
  id
  isFollowing
  isProfileOwner
  location
  locationUrl
  url
  username
  availabilityInfo {
    availabilityTimeline
    isAvailableFullTime
    isAvailableFreelance
  }
}
""",

}
