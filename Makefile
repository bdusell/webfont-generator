SHELL=/bin/bash

mkdirs=mkdir -p $1
mkfile={ $(call mkdirs,$(dir $1)) && touch $1; }

MKDIRS=$(call mkdirs,$(dir $@))
MKFILE=$(call mkfile,$@)
RM=rm -rf --

SFNTLY_PATH=sfntly

all: src/java/ConvertFont.class woff2/woff2_compress

# Clean generated files except for downloaded files
clean:
	$(RM) $(wildcard src/java/*.class)

# Clean all files, including downloads
clean-all: clean
	$(RM) $(SFNTLY_PATH)

.PHONY: all clean clean-all

.make/sfntly-src:
	svn checkout http://sfntly.googlecode.com/svn/trunk/ $(SFNTLY_PATH) && $(MKFILE)

.make/sfntly-build: .make/sfntly-src
	(cd $(SFNTLY_PATH)/java && ant) && $(MKFILE)

src/java/ConvertFont.class: src/java/ConvertFont.java .make/sfntly-build
	javac -cp src/java:sfntly/java/build/classes $<

woff2/Makefile:
	git clone http://github.com/google/woff2.git && \
	cd woff2 && \
	git submodule init && \
	git submodule update

woff2/woff2_compress:
	make -C woff2 clean all
