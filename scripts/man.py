#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import sys
import os.path
import datetime

ROOTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.realpath(ROOTDIR))

import gallery_dl.option  # noqa
import gallery_dl.version  # noqa


TEMPLATE = r""".TH "gallery-dl" "1" "$(date)s" "$(version)s" ""
.\" disable hyphenation
.nh

.SH NAME
gallery-dl \- download image-galleries and -collections

.SH SYNOPSIS
.B gallery-dl
[OPTION]... URL...

.SH DESCRIPTION
.B gallery-dl
is a command-line program to download image-galleries and -collections
from several image hosting sites. It is a cross-platform tool
with many configuration options and powerful filenaming capabilities.

.SH OPTIONS
%(options)s

.SH EXAMPLES
.TP
gallery-dl \f[I]URL\f[]
Download images from \f[I]URL\f[].
.TP
gallery-dl -g -u <username> -p <password> \f[I]URL\f[]
Print direct URLs from a site that requires authentication.
.TP
gallery-dl --filter 'type == "ugoira"' --range '2-4' \f[I]URL\f[]
Apply filter and range expressions. This will only download
the second, third, and fourth file where its type value is equal to "ugoira".
.TP
gallery-dl r:\f[I]URL\f[]
Scan \f[I]URL\f[] for other URLs and invoke \f[B]gallery-dl\f[] on them.
.TP
gallery-dl oauth:\f[I]SITE\-NAME\f[]
Gain OAuth authentication tokens for
.IR deviantart ,
.IR  flickr ,
.IR reddit ,
.IR smugmug ", and"
.IR tumblr .

.SH FILES
.TP
.I /etc/gallery-dl.conf
The system wide configuration file.
.TP
.I ~/.config/gallery-dl/config.json
Per user configuration file.
.TP
.I ~/.gallery-dl.conf
Alternate per user configuration file.

.SH BUGS
https://github.com/mikf/gallery-dl/issues

.SH AUTHORS
Mike Fährmann <mike_faehrmann@web.de>
.br
and https://github.com/mikf/gallery-dl/graphs/contributors

.SH "SEE ALSO"
.BR gallery-dl.conf (5)
"""

OPTS_FMT = r""".TP
.B "{}" {}
{}
"""


options = []
for action in gallery_dl.option.build_parser()._actions:
    if action.help.startswith("=="):
        continue
    options.append(OPTS_FMT.format(
        ", ".join(action.option_strings).replace("-", r"\-"),
        r"\f[I]{}\f[]".format(action.metavar) if action.metavar else "",
        action.help,
    ))

PATH = os.path.join(ROOTDIR, "gallery-dl.1")
with open(PATH, "w", encoding="utf-8") as file:
    file.write(TEMPLATE % {
        "options": "\n".join(options),
        "version": gallery_dl.version.__version__,
        "date"   : datetime.datetime.now(),
    })
