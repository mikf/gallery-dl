
PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
MANDIR ?= $(PREFIX)/man
SHAREDIR ?= $(PREFIX)/share
PYTHON ?= /usr/bin/env python3


all: man completion docs/supportedsites.rst

clean:
	$(RM) -r build/
	$(RM) -r data/

install: man completion
	$(PYTHON) setup.py install

release: man completion docs/supportedsites.rst
	scripts/release.sh

test:
	scripts/run_tests.sh

executable:
	scripts/pyinstaller.py

completion: data/completion/gallery-dl data/completion/_gallery-dl

man: data/man/gallery-dl.1 data/man/gallery-dl.conf.5

.PHONY: all clean install release test executable completion man

docs/supportedsites.rst: gallery_dl/*/*.py scripts/supportedsites.py
	$(PYTHON) scripts/supportedsites.py

data/man/gallery-dl.1: gallery_dl/option.py gallery_dl/version.py scripts/man.py
	$(PYTHON) scripts/man.py

data/man/gallery-dl.conf.5: docs/configuration.rst gallery_dl/version.py scripts/man.py
	$(PYTHON) scripts/man.py

data/completion/gallery-dl: gallery_dl/option.py scripts/completion_bash.py
	$(PYTHON) scripts/completion_bash.py

data/completion/_gallery-dl: gallery_dl/option.py scripts/completion_zsh.py
	$(PYTHON) scripts/completion_zsh.py
