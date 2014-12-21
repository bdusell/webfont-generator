Web Font Generator
------------------

One font goes in, all web fonts come out.

Usage
-----

The driver script is `generate-webfonts`. In the simplest use case, it accepts
a font file as its argument and spits out all of the converted fonts and a CSS
stylesheet containing the appropriate `@font-face` rule to the directory
specified by `-o`.

    ./generate-webfonts foo.ttf -o fonts/

Supported Formats
-----------------

`generate-webfonts` reads all formats readable by FontForge, which include ttf,
otf, svg, and woff. It cannot read eot.

Dependencies
------------

The generator leverages two third-party libraries for converting fonts.

* *sfntly* by Google, the open-source Java library which powers Google Fonts
* *FontForge*, a free, general-purpose, and scriptable font editor program

FontForge supports a large number of font formats but has no support for the
eot format. The blazingly fast sfntly library covers this gap.

Invoking `make` will attempt to install these libraries on your system.

The script `generate-webfonts` is written in Python and therefore requires
`python` to be installed on the system. The sfntly converter requires `javac`
and `ant` to build and `java` to run. Fetching the sfntly repository requires
`svn`.
