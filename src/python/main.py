#!/usr/bin/env python

import sys, os, os.path, re, shutil, subprocess, urllib, base64
from os.path import dirname
from subprocess import Popen, PIPE

VERSION = '1.2.2'

BASE_DIR = dirname(dirname(dirname(os.path.realpath(__file__))))

INPUT_FORMATS = ['ttf', 'otf', 'woff', 'svg']
INPUT_FORMAT_SET = set(INPUT_FORMATS)

class Error(RuntimeError):
    pass

class FontFile(object):

    def __init__(self, path, name, format):
        self.path = path
        self.name = name
        self.format = format

    def __repr__(self):
        return 'FontFile(%r, %r, %r)' % (self.path, self.name, self.format)

    def _file(self, format, output_dir):
        basename = os.path.basename(self.name)
        name = os.path.join(output_dir, basename)
        return FontFile(name + os.extsep + format, name, format)

    def _files(self, formats, output_dir):
        return { f : self._file(f, output_dir) for f in formats }

    def basename(self):
        return os.path.basename(self.path)

    def svg_id(self):
        return os.path.splitext(self.basename())[0]

    def copy(self, output_dir):
        result = self._file(self.format, output_dir)
        if copy_file(self.path, result.path):
            return result
        else:
            return self

    def convert_with_fontforge(self, formats, output_dir):
        results = self._files(formats, output_dir)
        convert_with_fontforge(self.path, (f.path for f in results.itervalues()))
        return results

    def convert_with_sfntly(self, formats, output_dir):
        results = self._files(formats, output_dir)
        convert_with_sfntly(self.path, (f.path for f in results.itervalues()))
        return results

    def convert_with_woff2(self, formats, output_dir):
        if not formats:
            return {}
        convert_with_woff2(self.path)
        return self._files(formats, output_dir)

def make_dirs(path):
    try:
        os.makedirs(path)
    except os.error:
        pass

def make_file_dirs(path):
    make_dirs(dirname(path))

def copy_file(input_name, output_name):
    make_file_dirs(output_name)
    try:
        shutil.copy(input_name, output_name)
    except shutil.Error as e:
        if not e.message.endswith(' are the same file'):
            raise Error(e.message)
        return False
    return True

def escape(s):
    return s.replace('"', '\\"')

def devnull(mode):
    return open(os.devnull, mode)

def indent(s, tab):
    return '\n'.join(tab + line for line in s.split('\n'))

def convert_with_fontforge(input_name, output_names):
    output_names = list(output_names)
    if not output_names:
        return
    make_file_dirs(next(iter(output_names)))
    with devnull('w') as out:
        p = Popen(['fontforge', '-lang=ff', '-script', '-'],
                stdin=PIPE, stdout=out, stderr=PIPE)
        p.stdin.write('Open("%s")\n' % escape(input_name))
        for output_name in output_names:
            p.stdin.write('Generate("%s")\n' % escape(output_name))
        p.stdin.close()
        err = p.stderr.read()
        p.stderr.close()
        if p.wait() != 0:
            raise Error('FontForge conversion failed:\n\n' + indent(err, '  '))

SFNTLY_PATHS = ['src/java', 'vendor/sfntly/java/build/classes']
SFNTLY_CLASSPATH = ':'.join(os.path.join(BASE_DIR, p) for p in SFNTLY_PATHS)

def convert_with_sfntly(input_name, output_names):
    output_names = list(output_names)
    if not output_names:
        return
    make_file_dirs(next(iter(output_names)))
    command = ['java', '-cp', SFNTLY_CLASSPATH, 'ConvertFont', input_name]
    for output_name in output_names:
        command.append('-o')
        command.append(output_name)
    if subprocess.call(command) != 0:
        raise Error('sfntly conversion failed')

WOFF2_COMPRESS_PATH = os.path.join(BASE_DIR, 'vendor/woff2/woff2_compress')

def convert_with_woff2(input_name):
    with devnull('rw') as fio:
        code = subprocess.call(
            [WOFF2_COMPRESS_PATH, input_name],
            stdin=fio, stdout=fio, stderr=fio)
        if code != 0:
            raise Error('woff2 conversion failed')

FONTFORGE_OUTPUT_FORMATS = set(['ttf', 'svg'])
SFNTLY_OUTPUT_FORMATS = set(['woff', 'eot'])
WOFF2_OUTPUT_FORMATS = set(['woff2'])
OUTPUT_FORMATS = (
    FONTFORGE_OUTPUT_FORMATS |
    SFNTLY_OUTPUT_FORMATS |
    WOFF2_OUTPUT_FORMATS)

def generate_fonts(input_files, output_formats, output_dir):
    output_format_set = set(output_formats)
    unrecognized_formats = (
        output_format_set.difference(input_files) - OUTPUT_FORMATS)
    if unrecognized_formats:
        raise Error('unable to convert to format ' + ', '.join(unrecognized_formats))
    if 'woff2' in output_format_set:
        output_format_set.add('ttf')
    file_pool = {}
    for f in input_files:
        file_pool[f.format] = (f.copy(output_dir) if f.format in output_format_set else f)
    for format_ in INPUT_FORMATS:
        if format_ in file_pool:
            fontforge_input = file_pool[format_]
            break
    else:
        raise Error('no suitable input font')
    output_format_set.difference_update(file_pool)
    file_pool.update(
        fontforge_input.convert_with_fontforge(
            output_format_set & FONTFORGE_OUTPUT_FORMATS,
            output_dir))
    output_format_set -= FONTFORGE_OUTPUT_FORMATS
    ttf = file_pool['ttf']
    file_pool.update(
        ttf.convert_with_sfntly(output_format_set & SFNTLY_OUTPUT_FORMATS, output_dir))
    file_pool.update(
        ttf.convert_with_woff2(output_format_set & WOFF2_OUTPUT_FORMATS, output_dir))
    return file_pool

ESCAPE_CSS_STR_PAT = re.compile('(\')|(\\n)')

def _replace_css_str(m):
    quote, newline = m.groups()
    if quote:
        return '\\' + quote
    else:
        return '\\A'

def escape_css_str(s):
    return ESCAPE_CSS_STR_PAT.sub(_replace_css_str, s)

ESCAPE_CSS_URL_PAT = re.compile('([()\\s\'"])')

def escape_css_url(s):
    return ESCAPE_CSS_URL_PAT.sub('\\\\\\1', s)

def css_format(f):
    if f == 'eot':
        return 'embedded-opentype'
    elif f == 'ttf':
        return 'truetype'
    else:
        return f

MEDIA_TYPE_MAPPING = {
    'eot' : 'application/vnd.ms-fontobject',
    'otf' : 'application/font-sfnt',
    'svg' : 'image/svg+xml',
    'ttf' : 'application/font-sfnt',
    'woff' : 'application/font-woff',
    'woff2' : 'application/font-woff2'
}

def media_type(format):
    return MEDIA_TYPE_MAPPING[format]

def data_url(format, file_name):
    with open(file_name) as fin:
        data = fin.read()
    return 'data:%s;base64,%s' % (media_type(format), base64.b64encode(data))

def generate_css(file_name, formats, file_pool, prefix, font_family):
    if file_name is None:
        return
    formats = list(formats)
    output_str_prefix = '''\
@font-face {
  font-family: '%s';
  src: ''' % escape_css_str(font_family)
    output_font_strs = []
    try:
        formats.remove(('eot', False))
    except ValueError:
        pass
    else:
        eot_file = file_pool['eot']
        eot_url = escape_css_url(prefix + eot_file.basename())
        output_str_prefix += '''\
url(%s);
  src: ''' % eot_url
        output_font_strs.append("url(%s?#iefix) format('embedded-opentype')" % eot_url)
    for f, inline in formats:
        font_file = file_pool[f]
        if inline:
            url = data_url(f, font_file.path)
        else:
            url = escape_css_url(prefix + urllib.quote_plus(font_file.basename()))
        if f == 'svg':
            url += '#' + escape_css_url(urllib.quote(font_file.svg_id()))
        output_font_strs.append("url(%s) format('%s')" % (url, css_format(f)))
    output_str = output_str_prefix + ',\n       '.join(output_font_strs) + ';\n}\n'
    with (sys.stdout if file_name == '-' else open(file_name, 'w')) as fout:
        fout.write(output_str)

def _parse_output_formats(formats):
    for f in formats:
        inline = f.endswith(':inline')
        if inline:
            f = f[:-7]
        yield f, inline

def usage(out):
    out.write('''\
Usage: %s [options] <input-file> ...

  Convert font files to web-friendly font formats.

Arguments:
  <input-file> ...
                At least one input font file. Recognized formats are:
                  ttf, otf, woff, svg
                Given this list of input files, the converter will attempt to
                satisfy the output format requirements by copying matching
                input files and converting files to fill in the gaps.

Options:
  -o --output <dir>
                Destination directory for converted files. Even if only inline
                fonts are generated, a destination directory is needed to hold
                intermediate files.
  -f --format <formats>
                Comma-separated list of output formats.
                Possible formats are:
                  woff, woff2, ttf, eot, svg, otf
                Any format suffixed with `:inline` will cause the font to be
                inlined in the CSS file as a base64-encoded data URL, rather
                than a URL to a file.
                The default format list is: eot,woff2,woff,ttf,svg
  -c --css <file>
                Name of generated CSS file. Use `-` for stdout. Omit to
                generate no CSS.
  -p --prefix <prefix>
                Prefix of file paths in the generated CSS. Default is the name
                of the output directory.
  --family <name>
                Name of the font family used in the CSS file. Default is the
                base name of the first input file.
  -v --version  Display version.
  -h --help     Show this help message.
''' % sys.argv[0])

def main():
    input_file_names = []
    output_formats_str = None
    output_dir = None
    css_file_name = None
    prefix_str = None
    font_family = None
    args = sys.argv[:0:-1]
    while args:
        arg = args.pop()
        if arg == '-o' or arg == '--output':
            output_dir = args.pop()
        elif arg == '-f' or arg == '--format':
            output_formats_str = args.pop()
        elif arg == '-c' or arg == '--css':
            css_file_name = args.pop()
        elif arg == '-p' or arg == '--prefix':
            prefix_str = args.pop()
        elif arg == '--family':
            font_family = args.pop()
        elif arg == '-v' or arg == '--version':
            sys.stdout.write(VERSION + '\n')
            sys.exit(0)
        elif arg == '-h' or arg == '--help':
            usage(sys.stdout)
            sys.exit(0)
        elif arg == '--':
            input_file_names.extend(reversed(args))
            break
        else:
            input_file_names.append(arg)
    if not input_file_names or output_dir is None:
        usage(sys.stderr)
        sys.exit(1)
    input_files = []
    for input_file_name in input_file_names:
        name, ext = os.path.splitext(input_file_name)
        ext = ext[1:]
        if ext not in INPUT_FORMAT_SET:
            if ext:
                sys.stderr.write('Unrecognized format %r.\n\n' % ext)
            else:
                sys.stderr.write('Unrecognized format.\n\n')
            usage(sys.stderr)
            sys.exit(1)
        input_files.append(FontFile(input_file_name, name, ext))
    if output_formats_str is None:
        output_formats = ['eot', 'woff2', 'woff', 'ttf', 'svg']
    else:
        output_formats = output_formats_str.split(',')
    parsed_output_formats = list(_parse_output_formats(output_formats))
    if prefix_str is None:
        output_dir_parts = output_dir.split(os.sep)
        if not output_dir_parts[-1]:
            output_dir_parts.pop()
        if output_dir_parts:
            output_dir_parts.append('')
        prefix_str = '/'.join(output_dir_parts)
    if font_family is None:
        font_family = os.path.splitext(os.path.basename(input_file_names[0]))[0]
    try:
        file_pool = generate_fonts(
            input_files,
            set(f for f, inline in parsed_output_formats),
            output_dir)
        generate_css(
            css_file_name,
            parsed_output_formats,
            file_pool,
            prefix_str,
            font_family)
    except Error as e:
        sys.stderr.write(e.message + '\n')
        sys.exit(1)

if __name__ == '__main__':
    main()
