
PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
MANDIR ?= $(PREFIX)/man
SHAREDIR ?= $(PREFIX)/share
PYTHON ?= /usr/bin/env python3


all: man completion docs/supportedsites.rst

clean:
	$(RM) -r build/

install: man completion
	$(PYTHON) setup.py install

release: man completion docs/supportedsites.rst
	scripts/release.sh

test:
	scripts/run_tests.sh

executable:
	scripts/pyinstaller.py

completion: build/completion/gallery-dl

man: build/man/gallery-dl.1 build/man/gallery-dl.conf.5

.PHONY: all clean install release test executable completion man

docs/supportedsites.rst: gallery_dl/*/*.py scripts/supportedsites.py
	$(PYTHON) scripts/supportedsites.py

build/man/gallery-dl.1: gallery_dl/option.py gallery_dl/version.py scripts/man.py
	$(PYTHON) scripts/man.py

build/man/gallery-dl.conf.5: docs/configuration.rst gallery_dl/version.py scripts/man.py
	$(PYTHON) scripts/man.py

build/completion/gallery-dl: gallery_dl/option.py scripts/bash_completion.py
	$(PYTHON) scripts/bash_completion.py
