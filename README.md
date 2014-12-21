Web Font Generator
------------------

One font goes in, all web fonts come out.

Usage
-----

The driver script is `generate-webfonts`. In the simplest use case, it accepts
a font file as its argument and spits out all of the converted fonts and a CSS
stylesheet containing the appropriate `@font-face` rule to the directory
specified by `-o`.

    ./generate-webfonts -o fonts/ foo.ttf

The command above generates the following files:
* `fonts/foo.css`
* `fonts/foo.woff`
* `fonts/foo.ttf`
* `fonts/foo.eot`
* `fonts/foo.svg`

Options
-------

* `-h` `--help`: Show a help message.
* `-o` `--output`: Output directory where converted files will go.
* `-p` `--prefix`: Prefix of font paths used in the generated CSS. Default is
  "../assets/".
* `-f` `--family`: Font family name used in the generated CSS. Default is the
  base name of the input file.
* `-c` `--css`: Alternate destination path for the generated CSS file.

Supported Formats
-----------------

`generate-webfonts` reads all formats readable by FontForge, which include ttf,
otf, svg, and woff. It cannot read eot.

The generated font formats are woff, ttf, eot, and svg.

Dependencies
------------

The generator leverages two third-party libraries for converting fonts.

* *sfntly* by Google, the open-source Java library which powers Google Fonts
* *FontForge*, a free, general-purpose, and scriptable font editor program

FontForge supports a large number of font formats but has no support for the
eot format. The blazingly fast sfntly library covers this gap.

Invoking `make` will check out the sfntly repository locally where
`generate-webfonts` can find it.

The script `generate-webfonts` is written in Python and therefore requires
`python` to be installed on the system. The sfntly converter requires `javac`
and `ant` to build and `java` to run. Fetching the sfntly repository requires
`svn`.
