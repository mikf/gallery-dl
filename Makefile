
PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
MANDIR ?= $(PREFIX)/man
SHAREDIR ?= $(PREFIX)/share
PYTHON ?= /usr/bin/env python3


all: man completion supportedsites options

clean:
	$(RM) -r build/
	$(RM) -r data/

install: man completion
	$(PYTHON) setup.py install

release: man completion supportedsites
	scripts/release.sh

test:
	scripts/run_tests.py

executable:
	scripts/pyinstaller.py

completion: data/completion/gallery-dl data/completion/_gallery-dl data/completion/gallery-dl.fish

man: data/man/gallery-dl.1 data/man/gallery-dl.conf.5

supportedsites: docs/supportedsites.md

options: docs/options.md

.PHONY: all clean install release test executable completion man supportedsites options

docs/supportedsites.md: gallery_dl/*/*.py scripts/supportedsites.py
	$(PYTHON) scripts/supportedsites.py

docs/options.md: gallery_dl/option.py scripts/options.py
	$(PYTHON) scripts/options.py

data/man/gallery-dl.1: gallery_dl/option.py gallery_dl/version.py scripts/man.py
	$(PYTHON) scripts/man.py

data/man/gallery-dl.conf.5: docs/configuration.rst gallery_dl/version.py scripts/man.py
	$(PYTHON) scripts/man.py

data/completion/gallery-dl: gallery_dl/option.py scripts/completion_bash.py
	$(PYTHON) scripts/completion_bash.py

data/completion/_gallery-dl: gallery_dl/option.py scripts/completion_zsh.py
	$(PYTHON) scripts/completion_zsh.py

data/completion/gallery-dl.fish: gallery_dl/option.py scripts/completion_fish.py
	$(PYTHON) scripts/completion_fish.py
