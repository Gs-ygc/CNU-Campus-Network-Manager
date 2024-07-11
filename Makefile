prefix = /usr/local
bindir = $(prefix)/bin

PRG = CnuNet-bash.sh

install: $(PRG)
	install -D -m 755 $(PRG) $(DESTDIR)$(bindir)/CnuNet

uninstall:
	rm -f $(DESTDIR)$(bindir)/CnuNet
