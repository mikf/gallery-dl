
PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
MANDIR ?= $(PREFIX)/man
SHAREDIR ?= $(PREFIX)/share
PYTHON ?= /usr/bin/env python3

# set SYSCONFDIR to /etc if PREFIX=/usr or PREFIX=/usr/local
SYSCONFDIR = $(shell if [ $(PREFIX) = /usr -o $(PREFIX) = /usr/local ]; then echo /etc; else echo $(PREFIX)/etc; fi)

all: gallery-dl.1 gallery-dl.bash_completion docs/supportedsites.rst

clean:
	$(RM) gallery-dl.1 gallery-dl.bash_completion
	$(RM) -r build/

install: gallery-dl.1 gallery-dl.bash_completion
	$(PYTHON) setup.py install
	install -d $(DESTDIR)$(MANDIR)/man1
	install -m 644 youtube-dl.1 $(DESTDIR)$(MANDIR)/man1
	install -d $(DESTDIR)$(SYSCONFDIR)/bash_completion.d
	install -m 644 youtube-dl.bash_completion $(DESTDIR)$(SYSCONFDIR)/bash_completion.d/youtube-dl

release: docs/supportedsites.rst
	scripts/release.sh

test:
	scripts/run_tests.sh

.PHONY: all clean install release test

docs/supportedsites.rst: gallery_dl/*/*.py scripts/supportedsites.py
	$(PYTHON) scripts/supportedsites.py

gallery-dl.1: gallery_dl/option.py scripts/man.py
	$(PYTHON) scripts/man.py

gallery-dl.bash_completion: gallery_dl/option.py scripts/bash_completion.py
	$(PYTHON) scripts/bash_completion.py
