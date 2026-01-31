# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.


OtherPhotosQuery = """\
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
"""

OtherPhotosPaginationContainerQuery = """\
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
"""

ProfileRendererQuery = """\
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
"""

GalleriesDetailQueryRendererQuery = """\
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
"""

GalleriesDetailPaginationContainerQuery = """\
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
"""

LikedPhotosQueryRendererQuery = """\
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
"""

LikedPhotosPaginationContainerQuery = """\
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
"""
