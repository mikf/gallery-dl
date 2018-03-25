#!/bin/bash

TESTS_CORE=(config cookies downloader extractor oauth text util)
TESTS_RESULTS=(results)


# select tests
TESTS=()
case "${GALLERYDL_TESTS}" in
    core)    TESTS=( ${TESTS_CORE[@]}    );;
    results) TESTS=( ${TESTS_RESULTS[@]} );;
esac


# transform each array element to test_###.py
TESTS=( ${TESTS[@]/#/test_} )
TESTS=( ${TESTS[@]/%/.py}   )


# run 'nosetests' with selected tests
# (or all tests if ${TESTS} is empty)
nosetests --verbose -w test ${TESTS[@]}
