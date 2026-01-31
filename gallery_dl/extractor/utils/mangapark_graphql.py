# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.


Get_comicChapterList = """
query Get_comicChapterList($comicId: ID!) {
    get_comicChapterList(comicId: $comicId) {
        data {
            id
            dname
            title
            lang
            urlPath
            srcTitle
            sourceId
            dateCreate
        }
    }
}
"""

Get_chapterNode = """
query Get_chapterNode($getChapterNodeId: ID!) {
    get_chapterNode(id: $getChapterNodeId) {
        data {
            id
            dname
            lang
            sourceId
            srcTitle
            dateCreate
            comicNode{
                id
            }
            imageFile {
                urlList
            }
        }
    }
}
"""

Get_comicNode = """
query Get_comicNode($getComicNodeId: ID!) {
    get_comicNode(id: $getComicNodeId) {
        data {
            id
            name
            artists
            authors
            genres
        }
    }
}
"""

get_content_source_chapterList = """
  query get_content_source_chapterList($sourceId: Int!) {
    get_content_source_chapterList(
      sourceId: $sourceId
    ) {

  id
  data {


  id
  sourceId

  dbStatus
  isNormal
  isHidden
  isDeleted
  isFinal

  dateCreate
  datePublic
  dateModify
  lang
  volume
  serial
  dname
  title
  urlPath

  srcTitle srcColor

  count_images

  stat_count_post_child
  stat_count_post_reply
  stat_count_views_login
  stat_count_views_guest

  userId
  userNode {

  id
  data {

id
name
uniq
avatarUrl
urlPath

verified
deleted
banned

dateCreate
dateOnline

stat_count_chapters_normal
stat_count_chapters_others

is_adm is_mod is_vip is_upr

  }

  }

  disqusId


  }

    }
  }
"""

get_content_comic_sources = """
  query get_content_comic_sources($comicId: Int!, $dbStatuss: [String] = [], $userId: Int, $haveChapter: Boolean, $sortFor: String) {
    get_content_comic_sources(
      comicId: $comicId
      dbStatuss: $dbStatuss
      userId: $userId
      haveChapter: $haveChapter
      sortFor: $sortFor
    ) {

id
data{

  id

  dbStatus
  isNormal
  isHidden
  isDeleted

  lang name altNames authors artists

  release
  genres summary{code} extraInfo{code}

  urlCover600
  urlCover300
  urlCoverOri

  srcTitle srcColor

  chapterCount
  chapterNode_last {
    id
    data {
      dateCreate datePublic dateModify
      volume serial
      dname title
      urlPath
      userNode {
        id data {uniq name}
      }
    }
  }
}

    }
  }
"""
