import os.path
import errno
import shutil
import subprocess

from util import indent

_d = os.path.dirname

BASE_DIR = _d(_d(_d(os.path.realpath(__file__))))
VENDOR_DIR = os.path.join(BASE_DIR, 'vendor')

class FontFile(object):
    """Represents a font file in a particular format."""

    def __init__(self, full_path, path_without_extension, format):
        self.full_path = full_path
        self.path_without_extension = path_without_extension
        self.format = format

    def moved_and_converted_to(self, output_dir, format):
        basename_without_ext = os.path.basename(self.path_without_extension)
        new_path_without_ext = os.path.join(output_dir, basename_without_ext)
        new_full_path = new_path_without_ext + os.extsep + format
        return FontFile(new_full_path, new_path_without_ext, format)

    def svg_id(self):
        return os.path.basename(self.path_without_extension)

def ensure_directory_exists(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

def ensure_file_directory_exists(path):
    ensure_directory_exists(os.path.dirname(path))

def copy_file(input_files, output_files):
    print('copy')
    for input_file in input_files:
        for output_file in output_files:
            _copy_file(input_file.full_path, output_file.full_path)
            return

def _copy_file(input_path, output_path):
    ensure_file_directory_exists(output_path)
    try:
        shutil.copy(input_path, output_path)
    except shutil.Error as e:
        if not e.message.endswith(' are the same file'):
            raise Error(e.message)

def _devnull(mode):
    return open(os.devnull, mode)

def _ff_escape(s):
    return s.replace('"', '\\"')

def convert_with_fontforge(input_files, output_files):
    print('fontforge')
    for input_file in input_files:
        _convert_with_fontforge(
            input_file.full_path, (f.full_path for f in output_files))
        return

def _convert_with_fontforge(input_path, output_paths):
    output_paths = list(output_paths)
    ensure_file_directory_exists(output_paths[0])
    with _devnull('w') as fout:
        p = subprocess.Popen(['fontforge', '-lang=ff', '-script', '-'],
            stdin=subprocess.PIPE, stdout=fout, stderr=subprocess.PIPE)
        p.stdin.write(('Open("%s")\n' % _ff_escape(input_path)).encode('utf-8'))
        for output_path in output_paths:
            p.stdin.write(('Generate("%s")\n' % _ff_escape(output_path)).encode('utf-8'))
        p.stdin.close()
        err = p.stderr.read()
        p.stderr.close()
        if p.wait() != 0:
            raise Error('FontForge conversion failed:\n\n' + indent(err, '  '))

def convert_with_sfntly(input_files, output_files):
    print('sfntly')
    for input_file in input_files:
        _convert_with_sfntly(input_file.full_path, (f.full_path for f in output_files))

SFNTLY_CLASSPATH = ':'.join([
    os.path.join(BASE_DIR, 'src', 'java'),
    os.path.join(VENDOR_DIR, 'sfntly', 'java', 'build', 'classes')
])

def _convert_with_sfntly(input_path, output_paths):
    output_paths = list(output_paths)
    ensure_file_directory_exists(output_paths[0])
    command = ['java', '-cp', SFNTLY_CLASSPATH, 'ConvertFont', input_path]
    for output_path in output_paths:
        command.append('-o')
        command.append(output_path)
    if subprocess.call(command) != 0:
        raise Error('sfntly conversion failed')

def convert_with_woff2_compress(input_files, output_files):
    print('woff2_compress')
    for input_file in input_files:
        _convert_with_woff2_compress(input_file.full_path)
        return

WOFF2_COMPRESS_PATH = os.path.join(VENDOR_DIR, 'woff2', 'woff2_compress')

def _convert_with_woff2_compress(input_path):
    with _devnull('r') as fin, _devnull('w') as fout:
        code = subprocess.call([WOFF2_COMPRESS_PATH, input_path],
            stdin=fin, stdout=fout, stderr=fout)
        if code != 0:
            raise Error('conversion with woff2_compress failed')

def convert_with_woff2_decompress(input_files, output_files):
    print('woff2_decompress')
    for input_file in input_files:
        _convert_with_woff2_decompress(input_file.full_path)
        return

WOFF2_DECOMPRESS_PATH = os.path.join(VENDOR_DIR, 'woff2', 'woff2_decompress')

def _convert_with_woff2_decompress(input_name):
    with _devnull('r') as fin, _devnull('w') as fout:
        code = subprocess.call([WOFF2_DECOMPRESS_PATH, input_path],
            stdin=fin, stdout=fout, stderr=fout)
        if code != 0:
            raise Error('conversion with woff2_decompress failed')

