# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from . import extractor, config, text
import socketserver
import http.server
import json


FAVICON = (b"GIF87a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\xff\xff\xff,"
           b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;")


class HttpServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


class RequestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        """Handle GET requests"""
        path, _, query = self.path.partition("?")
        args = text.parse_query(query)

        if path == "/api/json" or path.startswith("/api/json/"):
            self._send_json(self.api_json(args))

        elif path == "/favicon.ico":
            self._send_data(FAVICON, "image/gif", 200)

        else:
            self._send_json({"error": "Not Found"}, 404)

    def api_json(self, args):
        urls = args.get("url", "").split(",")
        data = [self._extract_data(url) for url in urls]
        return {"data": data, "urls": urls}

    def _extract_data(self, url):
        extr = extractor.find(url)
        if not extr:
            return url, None, {"error": "No extractor found"}

        data = []
        try:
            for message in extr:
                data.append([
                    value.copy() if hasattr(value, "copy") else value
                    for value in message
                ])
        except Exception as exc:
            data.append((exc.__class__.__name__, str(exc)))

        return url, data, None

    def _send_data(self, data, mime, status=200):
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, data, status=200):
        """Send 'data' as JSON response"""
        data = json.dumps(data, separators=(',', ':')).encode()
        self._send_data(data, "application/json", status)


def run():
    bind = config.get(("server", "bind"), "127.0.0.1")
    port = config.get(("server", "port"), 6412)
    httpd = HttpServer((bind, port), RequestHandler)

    try:
        httpd.serve_forever()
    except BaseException:
        httpd.server_close()
        raise


if __name__ == '__main__':
    run()
