#!/usr/bin/env python
# -*- coding: UTF-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="gallery_dl",
    version="0.3.1",
    description="gallery- and image downloader",
    long_description="download image galleries from several image hosting platforms",
    url="https://github.com/mikf/gallery-dl",
    download_url="https://codeload.github.com/mikf/gallery-dl/zip/v0.3.1",
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
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
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
