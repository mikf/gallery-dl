# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.


GetProfileProjects = """\
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
"""

GetMoodboardItemsAndRecommendations = """\
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
"""
