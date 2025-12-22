# -*- coding: utf-8 -*-

# Copyright 2023-2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.linkedin.com/"""

from .common import Extractor, Message
from .. import text, exception
import re

BASE_PATTERN = r"(?:https?://)?(?:www\.)?linkedin\.com"


class LinkedinExtractor(Extractor):
    """Base class for LinkedIn extractors"""

    category = "linkedin"
    root = "https://www.linkedin.com"
    request_interval = (1.0, 2.0)
    archive_fmt = "{post_id}_{num}"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.item_url = match.group(0)

    def items(self):
        url = self.item_url

        # Remove querystring for simpler regex processing
        url_clean = url.split("?")[0]

        # Extract post ID from URL - support multiple LinkedIn URL formats
        post_id_match = (
            re.search(r"-(\d+)-[A-Za-z0-9]+$", url_clean) or
            re.search(r"/feed/update/urn:li:activity:(\d+)", url_clean)
        )

        if not post_id_match:
            self.log.error("Unable to extract post ID from URL")
            raise exception.StopExtraction()

        post_id = post_id_match.group(1)
        self.log.debug(f"Extracting content for post ID: {post_id}")

        # Make HTTP request only after URL validation
        page = self.request(url).text

        # Extract metadata
        metadata = self._extract_metadata(page, post_id)
        if not metadata:
            self.log.warning("Unable to extract metadata, using basic info")
            metadata = {"post_id": post_id}

        # Extract media data
        media_data = self._extract_media_data(page)
        if not media_data:
            self.log.info("No media content found in this post")
            return

        # Process ALL media items with proper sequencing
        if media_data:
            for index, media in enumerate(media_data):
                media_type = media.get("type", "unknown")
                media_url = media.get("url")

                if not media_url:
                    self.log.debug(f"Skipping media item without URL: {media}")
                    continue

                # Create file metadata for this specific item
                file_metadata = metadata.copy()
                file_metadata.update(
                    {
                        "media_type": media_type,
                        "media_url": media_url,
                        "post_id": post_id,
                        "num": index + 1,  # Add sequence number
                    }
                )

                # Add additional media-specific metadata
                if media_type == "video":
                    file_metadata.update(
                        {
                            "duration": media.get("duration"),
                            "width": media.get("width"),
                            "height": media.get("height"),
                        }
                    )
                elif media_type == "image":
                    file_metadata.update(
                        {
                            "width": media.get("width"),
                            "height": media.get("height"),
                        }
                    )

                # Determine filename and directory
                directory = self._format_directory(metadata)
                filename = self._format_filename(media, metadata, index)

                yield Message.Directory, directory, file_metadata
                yield (
                    Message.Url,
                    media_url,
                    {
                        **file_metadata,
                        "filename": filename,
                        "extension": self._get_extension(media_url,
                                                         media_type),
                    },
                )

    def _extract_metadata(self, page, post_id):
        """Extract post metadata"""
        metadata = {"post_id": post_id}

        # Extract title
        title_match = re.search(r"<title[^>]*>([^<]+)</title>", page)
        if title_match:
            title = text.unescape(title_match.group(1))
            # Clean up title
            title = re.sub(r"\s*\|\s*LinkedIn$", "", title)
            metadata["title"] = title

        # Extract description
        desc_patterns = [
            r'"description":\s*"([^"]+)"',
            r'<meta[^>]+name=["\']description["\'][^>]+'
            r'content=["\']([^"\']+)["\']',
            r'"text":\s*"([^"]{50,})"',  # Longer text fields
        ]

        for pattern in desc_patterns:
            match = re.search(pattern, page)
            if match:
                description = text.unescape(match.group(1))
                # Filter out short/irrelevant descriptions
                if len(description) > 20:
                    metadata["description"] = description
                    break

        # Extract author/username
        author_patterns = [
            r'"author":\s*"([^"]+)"',
            r'"name":\s*"([^"]+)"',
            r'linkedin\.com/in/([^/?"]+)',
        ]

        for pattern in author_patterns:
            match = re.search(pattern, page)
            if match:
                author = text.unescape(match.group(1))
                if not author.startswith("http"):  # Filter out URLs
                    metadata["author"] = author
                    metadata["username"] = author.lower().replace(" ",
                                                                  "_")
                    break

        # Extract publication date
        date_patterns = [
            r'"datePublished":\s*"([^"]+)"',
            r'"publishTime":\s*"(\d+)"',
            r'"dateCreated":\s*"([^"]+)"',
        ]

        for pattern in date_patterns:
            match = re.search(pattern, page)
            if match:
                metadata["date"] = text.unescape(match.group(1))
                break

        # Extract post text content
        text_patterns = [
            r'"commentary":\s*"([^"]{30,})"',
            r'"text":\s*"([^"]{50,})"',
            r"<p[^>]*>([^<]{30,})</p>",
        ]

        for pattern in text_patterns:
            match = re.search(pattern, page)
            if match:
                post_text = text.unescape(match.group(1))
                if len(post_text) > 30:
                    metadata["post_text"] = post_text
                    break

        return metadata if any(k != "post_id" for k in metadata.keys()) \
            else None

    def _extract_media_data(self, page):
        """Extract video and image data from the page"""
        media_data = []

        # Method 1: Look for any URL fields and filter for media content
        url_patterns = [
            r'"url":\s*"([^"]+)"',
            r'"src":\s*"([^"]+)"',
            r'"videoUrl":\s*"([^"]+)"',
            r'"image":\s*"([^"]+)"',
            r'"contentUrl":\s*"([^"]+)"',
        ]

        for pattern in url_patterns:
            matches = re.findall(pattern, page, re.IGNORECASE)
            for match in matches:
                media_url = text.unescape(match)

                # Check if this is a media URL by looking for media indicators
                url_lower = media_url.lower()
                is_video = (
                    any(
                        indicator in url_lower
                        for indicator in ["mp4", "mov", "avi", "webm", "video"]
                    ) or
                    "dms.licdn.com/playlist/vid/" in url_lower or
                    "/vid/" in url_lower
                )
                is_image = (
                    any(
                        indicator in url_lower
                        for indicator in ["jpg", "jpeg", "png", "gif", "webp"]
                    ) or
                    "media.licdn.com/dms/image/" in url_lower
                )

                if is_video:
                    media_data.append(
                        {
                            "type": "video",
                            "url": media_url,
                            "width": None,
                            "height": None,
                        }
                    )
                    self.log.debug(f"Found video: {media_url}")
                elif is_image and self._is_post_content_image(media_url, page):
                    media_data.append(
                        {
                            "type": "image",
                            "url": media_url,
                            "width": None,
                            "height": None,
                        }
                    )
                    self.log.debug(f"Found image: {media_url}")

        # Remove duplicates and filter out poster images while preserving order
        seen_urls = set()
        unique_media = []
        for media in media_data:
            # Skip duplicates
            if media["url"] in seen_urls:
                continue

            # Skip poster images
            if self._should_skip_as_poster(media, page):
                continue

            seen_urls.add(media["url"])
            unique_media.append(media)

        return unique_media

    def _is_valid_media_url(self, url):
        """Check if URL is a valid media URL"""
        if not url or url.startswith(("data:", "blob:", "javascript:")):
            return False

        # Check for common media file extensions
        media_extensions = [
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".webp",
            ".mp4",
            ".mov",
            ".avi",
            ".webm",
        ]
        url_lower = url.lower()

        return any(ext in url_lower for ext in media_extensions)

    def _is_post_content_image(self, image_url, page):
        """Determine if an image is actual post content vs UI element"""
        # Skip LinkedIn's static assets and UI elements
        ui_patterns = [
            r"logo",
            r"icon",
            r"avatar",
            r"profile-picture",
            r"thumbnail",
            r"placeholder",
            r"sprite",
            r"branding",
            r"assets",
            r"static",
            r"common",
            r"ui-",
            r"btn-",
            r"nav-",
        ]

        url_lower = image_url.lower()
        if any(pattern in url_lower for pattern in ui_patterns):
            self.log.debug(f"Filtering out UI image: {image_url}")
            return False

        # Skip very small images (likely icons/thumbnails)
        if any(
            size in url_lower for size in ["24x24", "32x32", "48x48", "64x64",
                                           "16x16"]
        ):
            self.log.debug(f"Filtering out small image: {image_url}")
            return False

        # Skip profile pictures specifically
        if "profile-displayphoto" in url_lower:
            self.log.debug(f"Filtering out profile picture: {image_url}")
            return False

        # Check if image appears in post content area
        # Look for the image URL near post content indicators
        post_context_patterns = [
            r'"commentary"[^}]*' + re.escape(image_url),
            r'"text"[^}]*' + re.escape(image_url),
            r'"media"[^}]*' + re.escape(image_url),
            r'"content"[^}]*' + re.escape(image_url),
        ]

        for pattern in post_context_patterns:
            if re.search(pattern, page):
                self.log.debug(f"Image found in post context: {image_url}")
                return True

        # If we can't determine context, be conservative and include it
        # but log for debugging
        self.log.debug(f"Unable to determine context for image: {image_url}")
        return True

    def _is_thumbnail_or_ui(self, url):
        """Check if URL is likely a thumbnail or UI element"""
        url_lower = url.lower()

        # Common thumbnail/UI patterns
        thumbnail_patterns = [
            "thumb",
            "thumbnail",
            "small",
            "mini",
            "tiny",
            "logo",
            "icon",
            "avatar",
            "profile",
            "placeholder",
            "sprite",
            "branding",
            "asset",
            "static",
            "common",
        ]

        # Check for thumbnail indicators in URL
        for pattern in thumbnail_patterns:
            if pattern in url_lower:
                return True

        # Check for size indicators that suggest thumbnails
        size_patterns = [
            r"\d+x\d+",  # e.g., 100x100
            r"w\d+",  # e.g., w100
            r"h\d+",  # e.g., h100
            r"_s\.",  # e.g., _s.jpg
            r"_small\.",
        ]

        for pattern in size_patterns:
            if re.search(pattern, url_lower):
                return True

        return False

    def _should_skip_as_poster(self, media, page):
        """Check if media should be skipped as video poster image"""
        url = media["url"]
        url_lower = url.lower()

        # Skip feedshare-thumbnail URLs (video posters)
        if "feedshare-thumbnail" in url_lower:
            self.log.debug(f"Filtering video poster: {url}")
            return True

        return False

    def _format_directory(self, metadata):
        """Format directory path for downloaded files"""
        # Use username if available, otherwise "unknown_user"
        username = metadata.get("username", "unknown_user")

        # Clean username for filesystem
        username = re.sub(r"[^\w\-_.]", "_", username)

        # Create directory format: linkedin/{username}_{post_id}
        return f"linkedin/{username}_{metadata['post_id']}"

    def _format_filename(self, media, metadata, index):
        """Format filename for the media file with sequence numbering"""
        # Start with post ID
        base_name = metadata["post_id"]

        # Add media type
        media_type = media.get("type", "media")

        # Add sequence number in 01, 02 format
        sequence = f"{index + 1:02d}"

        # Result: 7403592769451335681_video_01, 7403592769451335681_image_02
        return f"{base_name}_{media_type}_{sequence}"

    def _get_extension(self, url, media_type):
        """Get file extension from URL or media type"""
        # Try to extract extension from URL
        url_lower = url.lower()
        for ext in [
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".webp",
            ".mp4",
            ".mov",
            ".avi",
            ".webm",
        ]:
            if url_lower.endswith(ext):
                return ext[1:]  # Remove the dot

        # Fallback to media type
        if media_type == "video":
            return "mp4"
        elif media_type == "image":
            return "jpg"

        return "bin"


class LinkedinPostExtractor(LinkedinExtractor):
    """Extractor for LinkedIn posts"""

    subcategory = "post"
    pattern = BASE_PATTERN + r"/posts/([^/?]+)"
    example = "https://www.linkedin.com/posts/username_activity-1234567890"


class LinkedinFeedExtractor(LinkedinExtractor):
    """Extractor for LinkedIn feed updates"""

    subcategory = "feed"
    pattern = BASE_PATTERN + r"/feed/update/urn:li:activity:(\d+)"
    example = ("https://www.linkedin.com/feed/update/urn:li:activity:"
               "7381400030911500288")
