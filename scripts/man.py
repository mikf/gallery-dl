#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2019-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Generate man pages"""

import re
import datetime

import util
import gallery_dl.option
import gallery_dl.version


def build_gallery_dl_1(path=None):

    OPTS_FMT = """.TP\n.B "{}" {}\n{}"""

    TEMPLATE = r"""
.TH "GALLERY-DL" "1" "%(date)s" "%(version)s" "gallery-dl Manual"
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
.IR flickr ,
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

    options = []
    for action in gallery_dl.option.build_parser()._actions:
        if action.help.startswith("=="):
            continue
        options.append(OPTS_FMT.format(
            ", ".join(action.option_strings).replace("-", r"\-"),
            r"\f[I]{}\f[]".format(action.metavar) if action.metavar else "",
            action.help,
        ))

    if not path:
        path = util.path("data/man/gallery-dl.1")
    with util.lazy(path) as file:
        file.write(TEMPLATE.lstrip() % {
            "options": "\n".join(options),
            "version": gallery_dl.version.__version__,
            "date"   : datetime.datetime.now().strftime("%Y-%m-%d"),
        })


def build_gallery_dl_conf_5(path=None):

    TEMPLATE = r"""
.TH "GALLERY-DL.CONF" "5" "%(date)s" "%(version)s" "gallery-dl Manual"
.\" disable hyphenation
.nh
.\" disable justification (adjust text to left margin only)
.ad l

.SH NAME
gallery-dl.conf \- gallery-dl configuration file

.SH DESCRIPTION
gallery-dl will search for configuration files in the following places
every time it is started, unless
.B --ignore-config
is specified:
.PP
.RS 4
.nf
.I /etc/gallery-dl.conf
.I $HOME/.config/gallery-dl/config.json
.I $HOME/.gallery-dl.conf
.fi
.RE
.PP
It is also possible to specify additional configuration files with the
.B -c/--config
command-line option or to add further option values with
.B -o/--option
as <key>=<value> pairs,

Configuration files are JSON-based and therefore don't allow any ordinary
comments, but, since unused keys are simply ignored, it is possible to utilize
those as makeshift comments by settings their values to arbitrary strings.

.SH EXAMPLE
{
.RS 4
"base-directory": "/tmp/",
.br
"extractor": {
.RS 4
"pixiv": {
.RS 4
"directory": ["Pixiv", "Works", "{user[id]}"],
.br
"filename": "{id}{num}.{extension}",
.br
"username": "foo",
.br
"password": "bar"
.RE
},
.br
"flickr": {
.RS 4
"_comment": "OAuth keys for account 'foobar'",
.br
"access-token": "0123456789-0123456789abcdef",
.br
"access-token-secret": "fedcba9876543210"
.RE
}
.RE
},
.br
"downloader": {
.RS 4
"retries": 3,
.br
"timeout": 2.5
.RE
}
.RE
}

%(options)s

.SH BUGS
https://github.com/mikf/gallery-dl/issues

.SH AUTHORS
Mike Fährmann <mike_faehrmann@web.de>
.br
and https://github.com/mikf/gallery-dl/graphs/contributors

.SH "SEE ALSO"
.BR gallery-dl (1)
"""

    sections = parse_docs_configuration()
    content = []

    for sec_name, section in sections.items():
        content.append(".SH " + sec_name.upper())

        for opt_name, option in section.items():
            content.append(".SS " + opt_name)

            for field, text in option.items():
                if field in ("Type", "Default"):
                    content.append('.IP "{}:" {}'.format(field, len(field)+2))
                    content.append(strip_rst(text))
                else:
                    content.append('.IP "{}:" 4'.format(field))
                    content.append(strip_rst(text, field != "Example"))

    if not path:
        path = util.path("data/man/gallery-dl.conf.5")
    with util.lazy(path) as file:
        file.write(TEMPLATE.lstrip() % {
            "options": "\n".join(content),
            "version": gallery_dl.version.__version__,
            "date"   : datetime.datetime.now().strftime("%Y-%m-%d"),
        })


def parse_docs_configuration():

    doc_path = util.path("docs", "configuration.rst")
    with open(doc_path, encoding="utf-8") as file:
        doc_lines = file.readlines()

    sections = {}
    sec_name = None
    options = None
    opt_name = None
    opt_desc = None
    name = None
    last = None
    for line in doc_lines:

        if line[0] == ".":
            continue

        # start of new section
        elif re.match(r"^=+$", line):
            if sec_name and options:
                sections[sec_name] = options
            sec_name = last.strip()
            options = {}

        # start of new option block
        elif re.match(r"^-+$", line):
            opt_name = last.strip()
            opt_desc = {}

        # end of option block
        elif opt_name and opt_desc and line == "\n" and not last:
            options[opt_name] = opt_desc
            opt_name = None
            name = None

        # inside option block
        elif opt_name:
            if line[0].isalpha():
                name = line.strip()
                opt_desc[name] = ""
            else:
                line = line.strip()
                if line.startswith(("* ", "- ")):
                    # list item
                    line = ".br\n" + line
                elif line.startswith("| "):
                    # line block
                    line = line[2:] + "\n.br"
                opt_desc[name] += line + "\n"

        last = line
    sections[sec_name] = options

    return sections


def strip_rst(text, extended=True, *, ITALIC=r"\\f[I]\1\\f[]", REGULAR=r"\1"):

    text = text.replace("\\", "\\\\")

    # ``foo``
    repl = ITALIC if extended else REGULAR
    text = re.sub(r"``([^`]+)``", repl, text)
    # |foo|_
    text = re.sub(r"\|([^|]+)\|_*", ITALIC, text)
    # `foo <bar>`__
    text = re.sub(r"`([^`<]+) <[^>`]+>`_+", ITALIC, text)
    # `foo`_
    text = re.sub(r"`([^`]+)`_+", ITALIC, text)
    # `foo`
    text = re.sub(r"`([^`]+)`", REGULAR, text)
    # foo_
    text = re.sub(r"([A-Za-z0-9-]+)_+(?=\s)", ITALIC, text)
    # -------
    text = re.sub(r"---+", "", text)

    return text


if __name__ == "__main__":
    build_gallery_dl_1()
    build_gallery_dl_conf_5()
