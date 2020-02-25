#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

TESTS_CORE=(cache config cookies downloader extractor oauth postprocessor text util)
TESTS_RESULTS=(results)


# select tests
case "${1:-${GALLERYDL_TESTS:-core}}" in
    core)    TESTS=( ${TESTS_CORE[@]}    );;
    results) TESTS=( ${TESTS_RESULTS[@]} );;
    *)       TESTS=(                     );;
esac


# transform each array element to test_###.py
TESTS=( ${TESTS[@]/#/test_} )
TESTS=( ${TESTS[@]/%/.py}   )


# run 'nosetests' with selected tests
# (or all tests if ${TESTS} is empty)
nosetests --verbose -w "${DIR}/../test" ${TESTS[@]}
