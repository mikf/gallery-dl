from .common import Extractor, Message, GalleryExtractor
from .. import text

BASE_PATTERN = r"(?:https?://)?redbust\.com"


class RedbustGalleryExtractor(GalleryExtractor):
    """Extractor for Redbust albums"""
    category = "redbust"
    pattern = BASE_PATTERN + r"/([\w-]*)/$"
    directory_fmt = ("{category}", "{gallery_id}")
    filename_fmt = "{filename}.{extension}"

    def __init__(self, match):
        self.root = text.root_from_url(match.group(0))
        self.gallery_url = match.group(0)
        self.gallery_id = match.group(1)
        GalleryExtractor.__init__(self, match, self.gallery_url)

    def metadata(self, page):
        """Return a dict with gallery metadata"""
        if not page:
            return {}
            
        title = text.extract(page, '<title>', '</title>')[0]
        if title:
            title = title.strip()
            
        return {
            "gallery_id": self.gallery_id,
            "title": title or self.gallery_id,
        }

    def images(self, page):
        """Return a list of all (image-url, metadata) tuples"""
        if not page:
            return []
            
        url_list = []
        img_tags = list(text.extract_iter(page, '<img ', '/>'))
        
        for img_tag in img_tags:
            # Skip non-gallery images (like navigation, logos, etc)
            if 'class="attachment-medium' not in img_tag and "class='attachment-medium" not in img_tag:
                continue
                
            # Extract the source URL
            img_src = text.extract(img_tag, 'src="', '"')[0]
            if not img_src:
                continue
                
            # Check if there's a srcset with larger images
            srcset = text.extract(img_tag, 'srcset="', '"')[0]
            if srcset:
                # Get the largest image (last one in srcset)
                srcset_urls = srcset.split(', ')
                if srcset_urls:
                    largest_url = srcset_urls[-1].split(' ')[0]
                    if largest_url:
                        img_src = largest_url
            
            # Create data dictionary
            data = {}
            data["filename"] = text.filename_from_url(img_src)
            url_list.append((img_src, data))
                
        return url_list


class RedbustExtractor(Extractor):
    """Extractor for Redbust Images"""
    category = "redbust"
    pattern = BASE_PATTERN + r"/([\w-]*)/([\w-]*)/$"
    directory_fmt = ("{category}", "{gallery}")
    filename_fmt = "{filename}.{extension}"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.gallery, self.image_id = match.groups()

    def items(self):
        """Return a list of all (image-url, metadata)-tuples"""
        pagetext = self.request(text.ensure_http_scheme(self.url)).text

        # Look for the largest image in srcset first
        srcset = text.extract(pagetext, 'srcset="', '"')[0]
        if srcset:
            # Extract the largest image from srcset (typically last one)
            srcset_urls = srcset.split(', ')
            img_url = srcset_urls[-1].split(' ')[0] if srcset_urls else None
        
        # Fallback to original extraction method
        if not srcset or not img_url:
            divdata = text.extract(pagetext, '<div class="entry-inner ', 'alt="')
            if not divdata or not divdata[0]:
                divdata = text.extract(pagetext, '<div class=\'entry-inner ', 'alt=\'')
            
            img_url = None
            if divdata and divdata[0]:
                img_url_data = text.extract(divdata[0], 'img src=\"', '\"')
                if not img_url_data or not img_url_data[0]:
                    img_url_data = text.extract(divdata[0], 'img src=\'', '\'')
                
                if img_url_data and img_url_data[0]:
                    img_url = img_url_data[0]
        
        if not img_url:
            return

        data = text.nameext_from_url(img_url, {"url": img_url})
        data["filename"] = self.image_id
        data["gallery"] = self.gallery

        yield Message.Directory, data
        yield Message.Url, img_url, data
