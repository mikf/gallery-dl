# Welcome to gallery-dl contributing guide <!-- omit in toc -->

Thank you for investing your time and talents in contributing to gallery-dl! Please note this contribution guide is in early stages and very much a work in progress.

## Code Changes

+ Pull Requests should come from your work-in-progress branch and could be associated with an issue as necessary.
+ Github Actions are in place to ensure Python compatibility and formatting. Specifically:
  + Python features are intended to maintain compatibility to Python 3.4 and up (beware of f-strings, walrus, etc)
  + flake8 will cause an action to fail (beware of E501 for example)
