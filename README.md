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
./setup # Fetch and build third-party libraries
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

Conceptually, given a list of input files and a list of output formats, the
converter will attempt to satisfy all output format requirements by copying
matching input files and converting files to fill in the gaps. Because of
limitations in the underlying font converters, some intermediate formats not
requested may be generated.

The command will avoid generating a file in a certain output format if a file
matching that format is already listed as one of the inputs. In this case, the
input file will simply be copied to the destination directory (or left alone,
if it is already in the output directory). If such a file is not listed in the
arguments, it will be overwritten with a newly converted file, even if it
already exists in the output directory.

See the options below for more advanced usage.

Syntax
------

The script `bin/generate-webfonts` accepts a list of font files as input and a
number of options:

### `-o --output`

Destination directory for converted files. Even if only inline
fonts are generated, a destination directory is needed to hold
intermediate files.

### `-f --format`

Comma-separated list of output formats. Possible formats are:

* ttf
* woff
* woff2
* eot
* svg
* otf

Any format suffixed with `:inline` will cause the font to be
inlined in the CSS file as a base64-encoded data URL, rather
than a URL to a file.

The default format list is `eot,woff2,woff,ttf,svg`.

### `-c --css`

Path for the generated CSS file. Use `-` for stdout. If omitted, no CSS is
generated.

### `-p --prefix`

Prefix of the font paths used in the generated CSS. For example, if your
stylesheet is served from `css/` and your fonts are served from `fonts/`, then
you will want to set the prefix to `../fonts/`. The default prefix is the name
of the output directory.

### `--font-family`

Name of the font family used in the CSS file. Default is the
base name of the first input file.

### `--verbose`

Show verbose output while running.

### `-v --version`

Display version.

Supported Formats
-----------------

`generate-webfonts` supports the following font formats:

* ttf
* woff
* woff2
* eot
* svg
* otf

It can convert to and from any of the formats listed above, with one
exception: it cannot convert eot to other formats.

Third-party Tools
-----------------

The generator leverages three third-party libraries/tools for converting fonts.
Since no single tool supports all font formats, the generator's job is to
figure out a good chain of converters to use to convert between any two font
formats. Under the hood, it's actually implemented as a shortest-paths problem
on a dependency graph.

The third-party tools used are:

* [FontForge](http://fontforge.github.io/en-US/), a free, general-purpose, and
  scriptable font editor program
* [sfntly](https://code.google.com/p/sfntly/) by Google, an open-source Java
  library which once powered Google Fonts
* Google's [woff2 converter](https://github.com/google/woff2)

FontForge supports reading and generating a good number of font formats,
although it has no support for the eot or woff2 formats. The blazingly fast
sfntly library can convert ttf fonts to eot or woff, covering one of these
gaps. The woff2 converter from Google is also used to convert between the
woff2 and ttf formats.

Setup
-----

As mentioned above, run `./setup` to download and build the third-party
libraries. Running `./setup` will check out the sfntly and woff2 converter
repositories locally where `generate-webfonts` can find them. Install
FontForge using your package manager or directly from their
[website](http://fontforge.github.io/en-US/).

The setup process assumes a \*nix environment. There is currently no support
for setting up this tool on Windows.

The following commands are required to run the setup script:
* `git`
* `java` and `javac`
* `mvn` (Maven)

The `generate-webfonts` script itself requires Python 3.

Closing Thoughts
----------------

Please convert responsibly! Respect font creators' copyrights.
