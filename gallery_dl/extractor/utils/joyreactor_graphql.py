# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.


IdPostPageQuery = """\
query IdPostPageQuery(
  $id: ID!
  $isAuthorised: Boolean!
) {
  node(id: $id) {
    __typename
    ... on Post {
      id
      user {
        id
      }
      text
      nsfw
      unsafe
      seoAttributes {
        title
        description
        ocr
        similarPosts
      }
      ...Post_post_2lIf9C
      comments {
        ...CommentTree_comments_48QSE5
        id
      }
      tags {
        ...TagList_blogs
        id
      }
    }
    id
  }
}

fragment AttributeEmbed_attribute on AttributeEmbed {
  __isAttributeEmbed: __typename
  type
  value
  image {
    comment
    id
  }
}

fragment AttributePicture_attribute on AttributePicture {
  __isAttributePicture: __typename
  id
  type
  insertId
  image {
    width
    height
    type
    comment
    hasVideo
    id
  }
}

fragment AttributePicture_post on Post {
  nsfw
  tags {
    name
    seoName
    synonyms
    id
  }
}

fragment Attribute_attribute on Attribute {
  __isAttribute: __typename
  type
  ...AttributePicture_attribute
  ...AttributeEmbed_attribute
}

fragment Attribute_post on Post {
  ...AttributePicture_post
}

fragment CommentTree_comments_2EWd0p on Comment {
  id
  locale
  level
  parent {
    __typename
    id
  }
  createdAt
  user {
    id
  }
  ...Comment_comment_2EWd0p
}

fragment CommentTree_comments_48QSE5 on Comment {
  id
  locale
  level
  parent {
    __typename
    id
  }
  createdAt
  user {
    id
  }
  ...Comment_comment_48QSE5
}

fragment CommentTree_post on Post {
  id
  ...Comment_post
}

fragment CommentVote_comment on Comment {
  id
  rating
  voted
}

fragment Comment_comment_2EWd0p on Comment {
  id
  user {
    id
    username
  }
  createdAt
  rating
  level
  contentVersion
  banned
  contentEditedAt
  locale
  ...EditableCommentContent_content
  ...Content_content
}

fragment Comment_comment_48QSE5 on Comment {
  id
  user {
    id
    username
  }
  createdAt
  rating
  level
  contentVersion
  banned
  contentEditedAt
  locale
  ...EditableCommentContent_content
  ...Content_content
  ...CommentVote_comment @include(if: $isAuthorised)
}

fragment Comment_post on Post {
  id
  ...Content_post
}

fragment Content_content on Content {
  __isContent: __typename
  text
  attributes {
    __typename
    id
    insertId
    ...Attribute_attribute
  }
}

fragment Content_post on Post {
  ...Attribute_post
}

fragment EditableCommentContent_content on Content {
  __isContent: __typename
  text
  attributes {
    __typename
    id
    insertId
    type
    image {
      id
      hasVideo
      type
      width
      height
    }
    ... on CommentAttributeEmbed {
      value
    }
  }
}

fragment Poll_post_2lIf9C on Post {
  id
  poll {
    question
    answers {
      id
      answer
      count
    }
    voted @include(if: $isAuthorised)
  }
}

fragment PostComments_post_2lIf9C on Post {
  id
  viewedCommentsAt @include(if: $isAuthorised)
  viewedCommentsCount @include(if: $isAuthorised)
  commentsCount
  user {
    id
  }
  unsafe
  ...CommentTree_post
}

fragment PostFooter_post_2lIf9C on Post {
  id
  commentsCount
  rating
  ratingGeneral
  createdAt
  viewedCommentsCount @include(if: $isAuthorised)
  favorite @include(if: $isAuthorised)
  ...PostVote_post @include(if: $isAuthorised)
}

fragment PostTags_post on Post {
  id
  user {
    id
  }
  postTags {
    deletable
    tag {
      id
      name
      seoName
      showAsCategory
      mainTag {
        id
        category {
          id
        }
        userTag {
          state
        }
      }
    }
  }
}

fragment PostVote_post on Post {
  id
  rating
  ratingGeneral
  minusThreshold
  vote {
    createdAt
    power
  }
}

fragment Post_post_2lIf9C on Post {
  id
  user {
    id
    username
  }
  bestComments {
    ...CommentTree_comments_2EWd0p
    id
  }
  tags {
    mainTag {
      id
      name
      category {
        id
      }
      userTag {
        state
      }
    }
    id
  }
  nsfw
  unsafe
  createdAt
  editableUntil
  text
  favorite @include(if: $isAuthorised)
  ...PostVote_post @include(if: $isAuthorised)
  banned
  poll {
    question
  }
  commentsCount
  ...CommentTree_post
  ...PostTags_post
  ...Content_post
  ...Content_content
  ...PostFooter_post_2lIf9C
  ...PostComments_post_2lIf9C
  ...Poll_post_2lIf9C
}

fragment TagList_blogs on Tag {
  id
  name
  seoName
  count
  subscribers
  showAsCategory
  mainTag {
    nsfw
    unsafe
    category {
      name
      id
    }
    id
  }
}
"""

TagPageQuery = """\
query TagPageQuery(
  $name: String
  $lineType: PostLineType!
  $favoriteType: PostLineType
  $page: Int
  $isAuthorised: Boolean!
  $isHomepage: Boolean!
) {
  tag(name: $name) {
    id
    name
    mainTag {
      id
      hierarchy {
        mainTag {
          name
          id
        }
        id
      }
      nsfw
      unsafe
      synonyms
      count
      seoName
      category {
        name
        unsafe
        nsfw
        id
      }
    }
    count
    postPager(type: $lineType, favoriteType: $favoriteType) {
      count
      id
    }
    ...TagHeader_blog @skip(if: $isHomepage)
    ...TagSidebar_blog @skip(if: $isHomepage)
    ...TagPostPager_blog_qTg8U
  }
}

fragment AttributeEmbed_attribute on AttributeEmbed {
  __isAttributeEmbed: __typename
  type
  value
  image {
    comment
    id
  }
}

fragment AttributePicture_attribute on AttributePicture {
  __isAttributePicture: __typename
  id
  type
  insertId
  image {
    width
    height
    type
    comment
    hasVideo
    id
  }
}

fragment AttributePicture_post on Post {
  nsfw
  tags {
    name
    seoName
    synonyms
    id
  }
}

fragment Attribute_attribute on Attribute {
  __isAttribute: __typename
  type
  ...AttributePicture_attribute
  ...AttributeEmbed_attribute
}

fragment Attribute_post on Post {
  ...AttributePicture_post
}

fragment BlogDescription_blog on Tag {
  id
  articlePost {
    ...Content_post
    ...Content_content
    id
  }
}

fragment CommentTree_comments_2EWd0p on Comment {
  id
  locale
  level
  parent {
    __typename
    id
  }
  createdAt
  user {
    id
  }
  ...Comment_comment_2EWd0p
}

fragment CommentTree_post on Post {
  id
  ...Comment_post
}

fragment Comment_comment_2EWd0p on Comment {
  id
  user {
    id
    username
  }
  createdAt
  rating
  level
  contentVersion
  banned
  contentEditedAt
  locale
  ...EditableCommentContent_content
  ...Content_content
}

fragment Comment_post on Post {
  id
  ...Content_post
}

fragment Content_content on Content {
  __isContent: __typename
  text
  attributes {
    __typename
    id
    insertId
    ...Attribute_attribute
  }
}

fragment Content_post on Post {
  ...Attribute_post
}

fragment EditableCommentContent_content on Content {
  __isContent: __typename
  text
  attributes {
    __typename
    id
    insertId
    type
    image {
      id
      hasVideo
      type
      width
      height
    }
    ... on CommentAttributeEmbed {
      value
    }
  }
}

fragment Poll_post_2lIf9C on Post {
  id
  poll {
    question
    answers {
      id
      answer
      count
    }
    voted @include(if: $isAuthorised)
  }
}

fragment PostComments_post_2lIf9C on Post {
  id
  viewedCommentsAt @include(if: $isAuthorised)
  viewedCommentsCount @include(if: $isAuthorised)
  commentsCount
  user {
    id
  }
  unsafe
  ...CommentTree_post
}

fragment PostFooter_post_2lIf9C on Post {
  id
  commentsCount
  rating
  ratingGeneral
  createdAt
  viewedCommentsCount @include(if: $isAuthorised)
  favorite @include(if: $isAuthorised)
  ...PostVote_post @include(if: $isAuthorised)
}

fragment PostPager_posts_3OSKdM on PostPager {
  posts(page: $page) {
    id
    nsfw
    unsafe
    tags {
      mainTag {
        id
        nsfw
        unsafe
        category {
          id
        }
        userTag {
          state
        }
      }
      id
    }
    user {
      username
      id
    }
    commentsCount
    ...Post_post_2lIf9C
  }
  count
  id
}

fragment PostTags_post on Post {
  id
  user {
    id
  }
  postTags {
    deletable
    tag {
      id
      name
      seoName
      showAsCategory
      mainTag {
        id
        category {
          id
        }
        userTag {
          state
        }
      }
    }
  }
}

fragment PostVote_post on Post {
  id
  rating
  ratingGeneral
  minusThreshold
  vote {
    createdAt
    power
  }
}

fragment Post_post_2lIf9C on Post {
  id
  user {
    id
    username
  }
  bestComments {
    ...CommentTree_comments_2EWd0p
    id
  }
  tags {
    mainTag {
      id
      name
      category {
        id
      }
      userTag {
        state
      }
    }
    id
  }
  nsfw
  unsafe
  createdAt
  editableUntil
  text
  favorite @include(if: $isAuthorised)
  ...PostVote_post @include(if: $isAuthorised)
  banned
  poll {
    question
  }
  commentsCount
  ...CommentTree_post
  ...PostTags_post
  ...Content_post
  ...Content_content
  ...PostFooter_post_2lIf9C
  ...PostComments_post_2lIf9C
  ...Poll_post_2lIf9C
}

fragment TagHeader_blog on Tag {
  id
  seoName
  name
  mainTag {
    id
    unsafe
    nsfw
    articlePost {
      id
    }
    ...BlogDescription_blog
    subTagsMenu {
      ...TagList_blogs
      id
    }
    subTags {
      ...TagList_blogs
      id
    }
    ...TagSuperBlogs_blog
    hierarchy {
      mainTag {
        id
        name
        showAsCategory
      }
      id
    }
    synonyms
    subscribers
    count
    image {
      id
    }
    userTag {
      state
    }
    articleImage {
      id
      type
    }
    category {
      id
      name
      category {
        id
      }
      showAsCategory
      nsfw
      unsafe
    }
    moderators {
      ...UserList_users
      id
    }
  }
  ...TagSidebar_blog
}

fragment TagList_blogs on Tag {
  id
  name
  seoName
  count
  subscribers
  showAsCategory
  mainTag {
    nsfw
    unsafe
    category {
      name
      id
    }
    id
  }
}

fragment TagPostPager_blog_qTg8U on Tag {
  unsafe
  postPager(type: $lineType, favoriteType: $favoriteType) {
    ...PostPager_posts_3OSKdM
    count
    id
  }
}

fragment TagSidebar_blog on Tag {
  name
  mainTag {
    subTagsMenu {
      id
    }
    subTags {
      ...TagList_blogs
      id
    }
    ...TagSuperBlogs_blog
    nsfw
    unsafe
    category {
      id
      name
      category {
        id
      }
      nsfw
      unsafe
    }
    moderators {
      ...UserList_users
      id
    }
    id
  }
}

fragment TagSuperBlogs_blog on Tag {
  subTagsMenu {
    id
    name
    nsfw
    unsafe
    showAsCategory
  }
}

fragment UserList_users on User {
  id
  username
}
"""

UserProfilePageQuery = """\
query UserProfilePageQuery(
  $username: String!
  $page: Int
  $isAuthorised: Boolean!
  $selfOrAdmin: Boolean!
) {
  user(username: $username) {
    id
    postPager {
      ...PostPager_posts_3OSKdM
      count
      id
    }
    ...UserSidebar_user_2lIf9C
    active @include(if: $selfOrAdmin)
    postsBannedUntil @include(if: $selfOrAdmin)
    commentsBannedUntil @include(if: $selfOrAdmin)
    tagBans @include(if: $selfOrAdmin) {
      tag {
        id
        name
      }
      bannedUntil
    }
    donatedLeft @include(if: $selfOrAdmin)
    goldStatusExpire @include(if: $selfOrAdmin)
    platinumStatusExpire @include(if: $selfOrAdmin)
    settings @include(if: $selfOrAdmin) {
      goldStatusExtend
    }
    userState @include(if: $isAuthorised)
  }
  me {
    goldStatus
    platinumStatus
    id
  }
}

fragment AttributeEmbed_attribute on AttributeEmbed {
  __isAttributeEmbed: __typename
  type
  value
  image {
    comment
    id
  }
}

fragment AttributePicture_attribute on AttributePicture {
  __isAttributePicture: __typename
  id
  type
  insertId
  image {
    width
    height
    type
    comment
    hasVideo
    id
  }
}

fragment AttributePicture_post on Post {
  nsfw
  tags {
    name
    seoName
    synonyms
    id
  }
}

fragment Attribute_attribute on Attribute {
  __isAttribute: __typename
  type
  ...AttributePicture_attribute
  ...AttributeEmbed_attribute
}

fragment Attribute_post on Post {
  ...AttributePicture_post
}

fragment CommentTree_comments_2EWd0p on Comment {
  id
  locale
  level
  parent {
    __typename
    id
  }
  createdAt
  user {
    id
  }
  ...Comment_comment_2EWd0p
}

fragment CommentTree_post on Post {
  id
  ...Comment_post
}

fragment Comment_comment_2EWd0p on Comment {
  id
  user {
    id
    username
  }
  createdAt
  rating
  level
  contentVersion
  banned
  contentEditedAt
  locale
  ...EditableCommentContent_content
  ...Content_content
}

fragment Comment_post on Post {
  id
  ...Content_post
}

fragment Content_content on Content {
  __isContent: __typename
  text
  attributes {
    __typename
    id
    insertId
    ...Attribute_attribute
  }
}

fragment Content_post on Post {
  ...Attribute_post
}

fragment EditableCommentContent_content on Content {
  __isContent: __typename
  text
  attributes {
    __typename
    id
    insertId
    type
    image {
      id
      hasVideo
      type
      width
      height
    }
    ... on CommentAttributeEmbed {
      value
    }
  }
}

fragment Poll_post_2lIf9C on Post {
  id
  poll {
    question
    answers {
      id
      answer
      count
    }
    voted @include(if: $isAuthorised)
  }
}

fragment PostComments_post_2lIf9C on Post {
  id
  viewedCommentsAt @include(if: $isAuthorised)
  viewedCommentsCount @include(if: $isAuthorised)
  commentsCount
  user {
    id
  }
  unsafe
  ...CommentTree_post
}

fragment PostFooter_post_2lIf9C on Post {
  id
  commentsCount
  rating
  ratingGeneral
  createdAt
  viewedCommentsCount @include(if: $isAuthorised)
  favorite @include(if: $isAuthorised)
  ...PostVote_post @include(if: $isAuthorised)
}

fragment PostPager_posts_3OSKdM on PostPager {
  posts(page: $page) {
    id
    nsfw
    unsafe
    tags {
      mainTag {
        id
        nsfw
        unsafe
        category {
          id
        }
        userTag {
          state
        }
      }
      id
    }
    user {
      username
      id
    }
    commentsCount
    ...Post_post_2lIf9C
  }
  count
  id
}

fragment PostTags_post on Post {
  id
  user {
    id
  }
  postTags {
    deletable
    tag {
      id
      name
      seoName
      showAsCategory
      mainTag {
        id
        category {
          id
        }
        userTag {
          state
        }
      }
    }
  }
}

fragment PostVote_post on Post {
  id
  rating
  ratingGeneral
  minusThreshold
  vote {
    createdAt
    power
  }
}

fragment Post_post_2lIf9C on Post {
  id
  user {
    id
    username
  }
  bestComments {
    ...CommentTree_comments_2EWd0p
    id
  }
  tags {
    mainTag {
      id
      name
      category {
        id
      }
      userTag {
        state
      }
    }
    id
  }
  nsfw
  unsafe
  createdAt
  editableUntil
  text
  favorite @include(if: $isAuthorised)
  ...PostVote_post @include(if: $isAuthorised)
  banned
  poll {
    question
  }
  commentsCount
  ...CommentTree_post
  ...PostTags_post
  ...Content_post
  ...Content_content
  ...PostFooter_post_2lIf9C
  ...PostComments_post_2lIf9C
  ...Poll_post_2lIf9C
}

fragment TagList_blogs on Tag {
  id
  name
  seoName
  count
  subscribers
  showAsCategory
  mainTag {
    nsfw
    unsafe
    category {
      name
      id
    }
    id
  }
}

fragment UserAwards_awardUser on AwardUser {
  award {
    id
    name
    description
    picUrl
    nextAward {
      id
    }
  }
  hidden
}

fragment UserList_users on User {
  id
  username
}

fragment UserSidebar_user_2lIf9C on User {
  id
  username
  rating
  ratingWeek
  hideSubscriptionsRatings
  commentNum
  postNum
  goodPostNum
  bestPostNum
  about
  createdAt
  sequentialVisits
  totalVisits
  lastVisit
  canSendPrivateMessage @include(if: $isAuthorised)
  awards {
    ...UserAwards_awardUser
  }
  subscribedTags {
    ...TagList_blogs
    id
  }
  moderatedTags {
    ...TagList_blogs
    id
  }
  blockedTags {
    ...TagList_blogs
    id
  }
  friends {
    ...UserList_users
    id
  }
  blockedUsers {
    ...UserList_users
    id
  }
  topTagRatings {
    ...UserTagRatings_favoriteTag
  }
}

fragment UserTagRatings_favoriteTag on UserTag {
  tag {
    id
    name
    nsfw
    unsafe
    showAsCategory
  }
  rating
}
"""

SearchPageQuery = """\
query SearchPageQuery(
  $query: String!
  $showNsfw: Boolean
  $showUnsafe: Boolean
  $showOnlyNsfw: Boolean
  $tagNames: [String!]
  $username: String
  $page: Int
  $isAuthorised: Boolean!
  $minRating: Int
  $maxRating: Int
  $sortByRating: Boolean
  $sortByDate: Boolean
) {
  search(query: $query, showNsfw: $showNsfw, showUnsafe: $showUnsafe, \
  showOnlyNsfw: $showOnlyNsfw, username: $username, tagNames: $tagNames, \
  sortByDate: $sortByDate, sortByRating: $sortByRating, minRating: \
  $minRating, maxRating: $maxRating) {
    tags {
      ...TagList_blogs
      mainTag {
        id
        unsafe
      }
      id
    }
    postPager {
      ...PostPager_posts_3OSKdM
      count
      id
    }
    similarQueries @skip(if: $isAuthorised)
  }
}

fragment AttributeEmbed_attribute on AttributeEmbed {
  __isAttributeEmbed: __typename
  type
  value
  image {
    comment
    id
  }
}

fragment AttributePicture_attribute on AttributePicture {
  __isAttributePicture: __typename
  id
  type
  insertId
  image {
    width
    height
    type
    comment
    hasVideo
    id
  }
}

fragment AttributePicture_post on Post {
  nsfw
  tags {
    name
    seoName
    synonyms
    id
  }
}

fragment Attribute_attribute on Attribute {
  __isAttribute: __typename
  type
  ...AttributePicture_attribute
  ...AttributeEmbed_attribute
}

fragment Attribute_post on Post {
  ...AttributePicture_post
}

fragment CommentTree_comments_2EWd0p on Comment {
  id
  locale
  level
  parent {
    __typename
    id
  }
  createdAt
  user {
    id
  }
  ...Comment_comment_2EWd0p
}

fragment CommentTree_post on Post {
  id
  ...Comment_post
}

fragment Comment_comment_2EWd0p on Comment {
  id
  user {
    id
    username
  }
  createdAt
  rating
  level
  contentVersion
  banned
  contentEditedAt
  locale
  ...EditableCommentContent_content
  ...Content_content
}

fragment Comment_post on Post {
  id
  ...Content_post
}

fragment Content_content on Content {
  __isContent: __typename
  text
  attributes {
    __typename
    id
    insertId
    ...Attribute_attribute
  }
}

fragment Content_post on Post {
  ...Attribute_post
}

fragment EditableCommentContent_content on Content {
  __isContent: __typename
  text
  attributes {
    __typename
    id
    insertId
    type
    image {
      id
      hasVideo
      type
      width
      height
    }
    ... on CommentAttributeEmbed {
      value
    }
  }
}

fragment Poll_post_2lIf9C on Post {
  id
  poll {
    question
    answers {
      id
      answer
      count
    }
    voted @include(if: $isAuthorised)
  }
}

fragment PostComments_post_2lIf9C on Post {
  id
  viewedCommentsAt @include(if: $isAuthorised)
  viewedCommentsCount @include(if: $isAuthorised)
  commentsCount
  user {
    id
  }
  unsafe
  ...CommentTree_post
}

fragment PostFooter_post_2lIf9C on Post {
  id
  commentsCount
  rating
  ratingGeneral
  createdAt
  viewedCommentsCount @include(if: $isAuthorised)
  favorite @include(if: $isAuthorised)
  ...PostVote_post @include(if: $isAuthorised)
}

fragment PostPager_posts_3OSKdM on PostPager {
  posts(page: $page) {
    id
    nsfw
    unsafe
    tags {
      mainTag {
        id
        nsfw
        unsafe
        category {
          id
        }
        userTag {
          state
        }
      }
      id
    }
    user {
      username
      id
    }
    commentsCount
    ...Post_post_2lIf9C
  }
  count
  id
}

fragment PostTags_post on Post {
  id
  user {
    id
  }
  postTags {
    deletable
    tag {
      id
      name
      seoName
      showAsCategory
      mainTag {
        id
        category {
          id
        }
        userTag {
          state
        }
      }
    }
  }
}

fragment PostVote_post on Post {
  id
  rating
  ratingGeneral
  minusThreshold
  vote {
    createdAt
    power
  }
}

fragment Post_post_2lIf9C on Post {
  id
  user {
    id
    username
  }
  bestComments {
    ...CommentTree_comments_2EWd0p
    id
  }
  tags {
    mainTag {
      id
      name
      category {
        id
      }
      userTag {
        state
      }
    }
    id
  }
  nsfw
  unsafe
  createdAt
  editableUntil
  text
  favorite @include(if: $isAuthorised)
  ...PostVote_post @include(if: $isAuthorised)
  banned
  poll {
    question
  }
  commentsCount
  ...CommentTree_post
  ...PostTags_post
  ...Content_post
  ...Content_content
  ...PostFooter_post_2lIf9C
  ...PostComments_post_2lIf9C
  ...Poll_post_2lIf9C
}

fragment TagList_blogs on Tag {
  id
  name
  seoName
  count
  subscribers
  showAsCategory
  mainTag {
    nsfw
    unsafe
    category {
      name
      id
    }
    id
  }
}
"""
