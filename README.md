Web Font Generator
------------------

One font goes in, all web fonts come out.

The purpose of this tool is to automate the generation of web-friendly font
formats and `@font-face` CSS rules from arbitrary font files, without having to
rely on web services or otherwise requiring a network connection.

See the
[Using @font-face article](http://css-tricks.com/snippets/css/using-font-face/)
on CSS-Tricks.com for more information about maximizing embedded font
compatibility.

Usage
-----

The driver script is `generate-webfonts`. At its most basic, it accepts a font
file as its argument and spits out all of the converted fonts and a CSS
stylesheet containing the appropriate `@font-face` rule to the directory
specified by `-o`.

    ./generate-webfonts -o assets foo.ttf

The command above generates the following files:
* `assets/foo.css`
* `assets/foo.woff`
* `assets/foo.ttf`
* `assets/foo.eot`
* `assets/foo.svg`

The file `assets/foo.css` will contain the following:

```css
@font-face {
  font-family: 'foo';
  src: url('assets/foo.eot');
  src: url('assets/foo.eot?#iefix') format('embedded-opentype'),
       url('assets/foo.woff') format('woff'),
       url('assets/foo.ttf') format('truetype'),
       url('assets/foo.svg#foo') format('svg');
}
```

See the options below for more advanced usage.

Options
-------

* `-h` `--help`: Show a help message.
* `-o` `--output`: Output directory where converted files will go.
* `-p` `--prefix`: Prefix of the font paths used in the generated CSS. For
  example, if your stylesheet is served from `css/` and your fonts from
  `fonts/`, then you will want to set the prefix to `../fonts/`. The default
  prefix is the name of the output directory.
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

* [sfntly](https://code.google.com/p/sfntly/) by Google, the open-source Java library which powers Google Fonts
* [FontForge](http://fontforge.github.io/en-US/), a free, general-purpose, and scriptable font editor program

FontForge supports a large number of font formats but has no support for the
eot format. The blazingly fast sfntly library covers this gap.

Invoking `make` will check out the sfntly repository locally where
`generate-webfonts` can find it. Install FontForge using your package manager
or directly from their [website](http://fontforge.github.io/en-US/).

The script `generate-webfonts` is written in Python and therefore requires
`python` to be installed on the system. The sfntly converter requires `javac`
and `ant` to build and `java` to run. Fetching the sfntly repository requires
`svn`.

Setup
-----

As mentioned above, run `make` to download sfntly and build the sfntly
converter, and install FontForge so that the `fontforge` command is available
to the driver script.

Closing Thoughts
----------------

Please convert responsibly! Respect font creators' copyrights. Do not use a
font which you are not licensed to use.
