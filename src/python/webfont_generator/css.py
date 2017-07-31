import re
import base64
import urllib.parse

ESCAPE_CSS_STR_PAT = re.compile('(\')|(\\n)')

def _replace_css_str(m):
    quote, newline = m.groups()
    if quote is not None:
        return '\\\''
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

def write_data_url(out, format, file_path):
    out.write('data:')
    out.write(media_type(format))
    out.write(';base64,')
    with open(file_path, 'rb') as fin:
        data = fin.read()
    out.write(base64.b64encode(data).decode('ascii'))

def _file_url(prefix, font_file):
    return escape_css_url(prefix + urllib.parse.quote_plus(font_file.basename()))

def generate_css(out, formats, output_files, prefix, font_family):
    formats = list(formats)
    out.write("""\
@font-face {
  font-family: '""")
    out.write(escape_css_str(font_family))
    out.write("""';
  src: """)
    try:
        # The eot file needs to be printed first
        formats.remove(('eot', False))
    except ValueError:
        first = True
    else:
        eot_url = _file_url(prefix, output_files['eot'])
        out.write('url(')
        out.write(eot_url)
        out.write(''');
  src: url(''')
        out.write(eot_url)
        out.write("?#iefix) format('embedded-opentype')")
        first = False
    for f, inline in formats:
        if first:
            first = False
        else:
            out.write(''',
       ''')
        out.write('url(')
        font_file = output_files[f]
        if inline:
            write_data_url(out, f, font_file.full_path)
        else:
            out.write(_file_url(prefix, font_file))
        if f == 'svg':
            out.write('#')
            out.write(escape_css_url(urllib.parse.quote(font_file.svg_id())))
        out.write(") format('")
        out.write(css_format(f))
        out.write("')")
    out.write(''';
}
''')
