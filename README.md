Web Font Generator
------------------

One font goes in, all web fonts come out.

The purpose of this tool is to automate the generation of web-friendly font
formats and `@font-face` CSS rules from arbitrary font files, without having to
rely on web services or otherwise requiring a network connection. This tool can
generate inline data URLs if needed.

See the
[Using @font-face article](http://css-tricks.com/snippets/css/using-font-face/)
on CSS-Tricks.com for more information about maximizing embedded font
compatibility.

Quickstart
----------

```sh
./setup.sh # Fetch and build third-party libraries
./bin/generate-webfonts MyFont.ttf -o assets/ # Convert a font
```

Usage
-----

The driver script is `generate-webfonts`. At its most basic, it accepts a font
file as its argument and spits out all of the converted fonts to a directory.
It can also generate CSS for the appropriate `@font-face` rule as well.

    ./bin/generate-webfonts -o assets MyFont.ttf --css MyFont.css

The command above, which uses the default output formats, generates the
following files:

* `MyFont.css`
* `assets/MyFont.woff`
* `assets/MyFont.woff2`
* `assets/MyFont.ttf`
* `assets/MyFont.eot`
* `assets/MyFont.svg`

The file `MyFont.css` will contain the following:

```css
@font-face {
  font-family: 'MyFont';
  src: url('assets/MyFont.eot');
  src: url('assets/MyFont.eot?#iefix') format('embedded-opentype'),
       url('assets/MyFont.woff2') format('woff2'),
       url('assets/MyFont.woff') format('woff'),
       url('assets/MyFont.ttf') format('truetype'),
       url('assets/MyFont.svg#foo') format('svg');
}
```

If you need to combine the css files you could always concatenate the output files or append them to your main css file:

```shell
cat assets/*.css >> build/main.css
```
If you need need transform a folder with some fonts and combine the css files you need run:
```shell
find your-font-dir/ -name '*.otf' -exec ./bin/generate-webfonts -o assets/ --css - '{}' ';' > main.css
```
Conceptually, given a list of input files and a list of output formats, the
converter will attempt to satisfy all output format requirements by copying
matching input files and converting files to fill in the gaps. Because of
limitations in the underlying font converters, some intermediate formats not
requested may be generated.

See the options below for more advanced usage.

Syntax
------

The script `bin/generate-webfonts` accepts a list of font files as input and a
number of options:

### `-h --help`

Diplay usage instructions.

### `-o --output`

Output directory where converted files will go. Even if only inline fonts are
generated, a destination directory is still needed to contain intermediate font
files.

### `-f --format`

Comma-separated list of output formats. Possible formats are `woff`, `woff2`,
`ttf`, `eot`, `svg`, `otf`.

Any format suffixed with `:inline` will cause the font to be inlined into the
CSS file as a base64-encoded data URL, rather than a URL to a file.

The default format list is `eot,woff2,woff,ttf,svg`.

### `-c --css`

Path for the generated CSS file. Use `-` for stdout. If omitted, no CSS is
generated.

### `-p --prefix`

Prefix of the font paths used in the generated CSS. For example, if your
stylesheet is served from `css/` and your fonts are served from `fonts/`, then
you will want to set the prefix to `../fonts/`. The default prefix is the name
of the output directory.

### `--family`

Font family name used in the generated CSS. Default is the base name of the
first input file.

### `-v --version`

Display the version.

Supported Formats
-----------------

`generate-webfonts` reads all formats readable by FontForge, which include ttf,
otf, svg, and woff. It cannot read eot.

The generated font formats are woff, woff2, ttf, eot, and svg.

Dependencies
------------

The generator leverages three third-party libraries for converting fonts.

* [FontForge](http://fontforge.github.io/en-US/), a free, general-purpose, and scriptable font editor program
* [sfntly](https://code.google.com/p/sfntly/) by Google, the open-source Java library which powers Google Fonts
* Google's [woff2 converter](https://github.com/google/woff2)

FontForge supports a good number of font formats but has no support for the
eot format. The blazingly fast sfntly library covers this gap.

Running `./setup.sh` will check out the sfntly and woff2 converter repositories
locally where `generate-webfonts` can find them. Install FontForge using your
package manager or directly from their
[website](http://fontforge.github.io/en-US/).

Other commands required to use this tool and its setup script are: `python`,
`java`, `javac`, `ant`, `git`, `svn`.

Setup
-----

As mentioned above, run `./setup.sh` to download and build the third-party
libraries.

Closing Thoughts
----------------

Please convert responsibly! Respect font creators' copyrights.
