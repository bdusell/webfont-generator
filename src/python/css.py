import re
import base64

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

def data_url(format, file_path):
    with open(file_path) as fin:
        data = fin.read()
    return 'data:%s;base64,%s' % (media_type(format), base64.b64encode(data))

def generate_css(file_name, formats, file_pool, prefix, font_family):
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
