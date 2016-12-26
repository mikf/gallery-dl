#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# get version without importing the package
exec(read("gallery_dl/version.py"))

setup(
    name="gallery_dl",
    version=__version__,
    description="Command-line program to download image galleries and collections from pixiv, exhentai, danbooru, gelbooru, nijie and more",
    long_description=read("README.rst"),
    url="https://github.com/mikf/gallery-dl",
    download_url="https://github.com/mikf/gallery-dl/releases/latest",
    author="Mike Fährmann",
    author_email="mike_faehrmann@web.de",
    maintainer="Mike Fährmann",
    maintainer_email="mike_faehrmann@web.de",
    license="GPLv2",
    python_requires=">=3.3",
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
    keywords="image gallery downloader crawler scraper",
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
