VERSION:=$(shell cat VERSION)
PACKAGE=Blit-$(VERSION)
TARBALL=$(PACKAGE).tar.gz
DOCROOT=Blit.org:public_html/tilestache/www

all: $(TARBALL)
	#

live: $(TARBALL)
	python setup.py upload

$(TARBALL):
	mkdir $(PACKAGE)
	ln setup.py $(PACKAGE)/
	ln README $(PACKAGE)/
	ln VERSION $(PACKAGE)/

	mkdir $(PACKAGE)/Blit
	ln Blit/*.py $(PACKAGE)/Blit/

	rm $(PACKAGE)/Blit/__init__.py
	cp Blit/__init__.py $(PACKAGE)/Blit/__init__.py
	perl -pi -e 's#\bN\.N\.N\b#$(VERSION)#' $(PACKAGE)/Blit/__init__.py

	tar -czf $(TARBALL) $(PACKAGE)
	rm -rf $(PACKAGE)

clean:
	find Blit -name '*.pyc' -delete
	rm -rf $(TARBALL) doc
