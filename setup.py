#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import os.path
import warnings
from setuptools import setup

if sys.hexversion < 0x3040000:
    sys.exit("Python 3.4+ required")


def read(fname):
    path = os.path.join(os.path.dirname(__file__), fname)
    with open(path, encoding="utf-8") as file:
        return file.read()

def check_file(fname):
    path = os.path.join(os.path.dirname(__file__), fname)
    if os.path.exists(path):
        return True
    warnings.warn(
        "Not including file '{}' since it is not present. "
        "Run 'make' to build all automatically generated files.".format(fname)
    )
    return False


# get version without importing the package
VERSION = re.search(
    r'__version__\s*=\s*"([^"]+)"',
    read("gallery_dl/version.py"),
).group(1)

FILES = [
    (path, [f for f in files if check_file(f)])
    for (path, files) in [
        ("share/bash-completion/completions", ["data/completion/gallery-dl"]),
        ("share/zsh/site-functions"         , ["data/completion/_gallery-dl"]),
        ("share/man/man1"                   , ["data/man/gallery-dl.1"]),
        ("share/man/man5"                   , ["data/man/gallery-dl.conf.5"]),
    ]
]


setup(
    name="gallery_dl",
    version=VERSION,
    description=("Command-line program to download image galleries and "
                 "collections from several image hosting sites"),
    long_description=read("README.rst"),
    url="https://github.com/mikf/gallery-dl",
    download_url="https://github.com/mikf/gallery-dl/releases/latest",
    author="Mike Fährmann",
    author_email="mike_faehrmann@web.de",
    maintainer="Mike Fährmann",
    maintainer_email="mike_faehrmann@web.de",
    license="GPLv2",
    python_requires=">=3.4",
    install_requires=[
        "requests>=2.11.0",
    ],
    extras_require={
        "video": [
            "youtube-dl",
        ],
    },
    packages=[
        "gallery_dl",
        "gallery_dl.extractor",
        "gallery_dl.downloader",
        "gallery_dl.postprocessor",
    ],
    entry_points={
        "console_scripts": [
            "gallery-dl = gallery_dl:main",
        ],
    },
    data_files=FILES,
    keywords="image gallery downloader crawler scraper",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Utilities",
    ],
    test_suite="test",
)
