# -*- coding: utf-8 -*-

from .common import Extractor, Message
from .. import text



class PicazorExtractor(Extractor):
    """Extractor for picazor.com"""
    category = "picazor"
    subcategory = "user"
    root = "https://picazor.com"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = "{id}_{order:>03}.{extension}"
    archive_fmt = "{id}_{order}"
    pattern = r"(?:https?://)?(?:www\.)?picazor\.com/en/([^/?#]+)"
    example = "https://picazor.com/en/USERNAME"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1)
        self.browser = "firefox"
        self.referer = f"{self.root}/en/{self.user}"

    def items(self):
        yield Message.Directory, "", {"category": self.category, "user": self.user}
        page = 1
        while True:
            url = f"{self.root}/api/files/{self.user}/sfiles"
            data = self.request_json(url, params={"page": page})
            
            if not data:
                break
                
            for item in data:
                path = item.get("path")
                if not path:
                    continue
                    
                file_url = f"{self.root}{path}"
                
                # Extract extension from path if possible, otherwise let nameext_from_url handle it
                # item["path"] example: /uploads/may25/sa31/kailey-mae/onlyfans/8i9u3/kailey-mae-onlyfans-p7ltb-12.jpg
                
                info = {
                    "user": self.user,
                    "id": item.get("id"),
                    "order": item.get("order"),
                    "subject_id": item.get("subject", {}).get("id"),
                    "subject_uri": item.get("subject", {}).get("uri"),
                    "visible": item.get("visible"),
                }
                
                text.nameext_from_url(file_url, info)
                
                yield Message.Url, file_url, info

            
            page += 1
