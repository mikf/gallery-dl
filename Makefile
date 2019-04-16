
PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
MANDIR ?= $(PREFIX)/man
SHAREDIR ?= $(PREFIX)/share
PYTHON ?= /usr/bin/env python3

# set SYSCONFDIR to /etc if PREFIX=/usr or PREFIX=/usr/local
SYSCONFDIR = $(shell if [ $(PREFIX) = /usr -o $(PREFIX) = /usr/local ]; then echo /etc; else echo $(PREFIX)/etc; fi)

all: man completion docs/supportedsites.rst

clean:
	$(RM) gallery-dl.1 gallery-dl.conf.5 gallery-dl.bash_completion
	$(RM) -r build/

install: man completion
	$(PYTHON) setup.py install

release: man completion docs/supportedsites.rst
	scripts/release.sh

test:
	scripts/run_tests.sh

executable:
	scripts/pyinstaller.py

completion: gallery-dl.bash_completion

man: gallery-dl.1 gallery-dl.conf.5

.PHONY: all clean install release test executable completion man

docs/supportedsites.rst: gallery_dl/*/*.py scripts/supportedsites.py
	$(PYTHON) scripts/supportedsites.py

gallery-dl.1: gallery_dl/option.py scripts/man.py
	$(PYTHON) scripts/man.py

gallery-dl.conf.5: docs/configuration.rst scripts/man.py
	$(PYTHON) scripts/man.py

gallery-dl.bash_completion: gallery_dl/option.py scripts/bash_completion.py
	$(PYTHON) scripts/bash_completion.py
