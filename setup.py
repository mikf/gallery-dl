#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os.path

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="gallery_dl",
    version="0.5.2",
    description="gallery- and image downloader",
    long_description=read("README.rst"),
    url="https://github.com/mikf/gallery-dl",
    download_url="https://github.com/mikf/gallery-dl/releases/latest",
    author="Mike Fährmann",
    author_email="mike_faehrmann@web.de",
    license="GPLv2",
    install_requires=[
        "requests >= 2.4.2",
    ],
    scripts=[
        "bin/gallery-dl",
    ],
    entry_points={
        'console_scripts': [
            'gallery-dl = gallery_dl:main',
        ],
    },
    packages=[
        "gallery_dl",
        "gallery_dl.extractor",
        "gallery_dl.downloader",
    ],
    keywords = "gallery crawler pixiv danbooru gelbooru exhentai",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Multimedia",
        "Topic :: Multimedia :: Graphics",
    ],
    test_suite='test',
)
