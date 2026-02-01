# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

AlbumGet = """
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

AlbumListOwnPictures = """
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

AlbumListWithPeek = """
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
