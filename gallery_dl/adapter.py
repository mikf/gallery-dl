# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Custom requests adapters"""

from requests.adapters import BaseAdapter
from requests import Response, codes
import io


class FileAdapter(BaseAdapter):

    def send(self, request, **kwargs):
        path = request.url[7:]
        response = Response()
        try:
            response.raw = open(path, "rb")
            response.raw.release_conn = response.raw.close
            response.status_code = codes.ok
        except IOError:
            response.raw = io.BytesIO()
            response.status_code = codes.bad_request
        return response

    def close(self):
        pass
