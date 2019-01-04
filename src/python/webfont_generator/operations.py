import os.path
import errno
import shutil
import subprocess

from .util import indent
from .error import Error

_d = os.path.dirname

BASE_DIR = _d(_d(_d(_d(os.path.realpath(__file__)))))
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

    def basename(self):
        return os.path.basename(self.full_path)

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

def copy_file(input_files, output_files, logger):
    for input_file in input_files:
        for output_file in output_files:
            input_path = input_file.full_path
            output_path = output_file.full_path
            logger.info('copying %s to %s' % (input_path, output_path))
            _copy_file(input_path, output_path)
            return

def _copy_file(input_path, output_path):
    ensure_file_directory_exists(output_path)
    try:
        shutil.copyfile(input_path, output_path)
    except shutil.SameFileError as e:
        pass

def _devnull(mode):
    return open(os.devnull, mode)

def _ff_escape(s):
    return s.replace('"', '\\"')

def convert_with_fontforge(input_files, output_files, logger):
    for input_file in input_files:
        input_path = input_file.full_path
        output_paths = [f.full_path for f in output_files]
        logger.info('using FontForge to convert %s to %s' % (input_path, ', '.join(output_paths)))
        _convert_with_fontforge(input_path, output_paths)
        return

def _convert_with_fontforge(input_path, output_paths):
    output_paths = list(output_paths)
    ensure_file_directory_exists(output_paths[0])
    with _devnull('w') as fout:
        p = subprocess.Popen(['fontforge', '-lang=ff', '-script', '-'],
            stdin=subprocess.PIPE, stdout=fout, stderr=subprocess.PIPE)
        # CIDFlatten flattens CID-based fonts (e.g. otf) with multiple
        # sub-fonts into one single font.
        # See https://github.com/bdusell/webfont-generator/issues/20
        p.stdin.write(('Open("%s")\nCIDFlatten()\n' % _ff_escape(input_path)).encode('utf-8'))
        for output_path in output_paths:
            p.stdin.write(('Generate("%s")\n' % _ff_escape(output_path)).encode('utf-8'))
        p.stdin.close()
        err = p.stderr.read()
        p.stderr.close()
        if p.wait() != 0:
            raise Error(
                'FontForge conversion failed:\n'
                'Output from FontForge:\n' +
                indent(err.decode('ascii'), '  '))
    # Ensure that the files were actually generated
    bad_files = [p for p in output_paths if not os.path.isfile(p)]
    if bad_files:
        raise Error(
            'FontForge failed to generate %s:\n'
            'Output from FontForge:\n'
            '%s' % (
                ', '.join(bad_files),
                indent(err.decode('ascii'), '  ')
            ))

def convert_with_sfntly(input_files, output_files, logger):
    for input_file in input_files:
        input_path = input_file.full_path
        output_paths = [f.full_path for f in output_files]
        logger.info('using sfntly to convert %s to %s' % (input_path, ', '.join(output_paths)))
        _convert_with_sfntly(input_path, output_paths)

SFNTLY_CLASSPATH = ':'.join([
    os.path.join(BASE_DIR, 'src', 'java'),
    os.path.join(VENDOR_DIR, 'sfntly', 'java', 'target', 'classes')
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

def convert_with_woff2_compress(input_files, output_files, logger):
    for input_file in input_files:
        input_path = input_file.full_path
        logger.info('using woff2_compress to convert %s to woff2' % input_path)
        _convert_with_woff2_compress(input_path)
        return

WOFF2_COMPRESS_PATH = os.path.join(VENDOR_DIR, 'woff2', 'woff2_compress')

def _convert_with_woff2_compress(input_path):
    with _devnull('r') as fin, _devnull('w') as fout:
        code = subprocess.call([WOFF2_COMPRESS_PATH, input_path],
            stdin=fin, stdout=fout, stderr=fout)
        if code != 0:
            raise Error('conversion with woff2_compress failed')

def convert_with_woff2_decompress(input_files, output_files, logger):
    for input_file in input_files:
        input_path = input_file.full_path
        logger.info('using woff2_decompress to convert %s to ttf' % input_path)
        _convert_with_woff2_decompress(input_path)
        return

WOFF2_DECOMPRESS_PATH = os.path.join(VENDOR_DIR, 'woff2', 'woff2_decompress')

def _convert_with_woff2_decompress(input_path):
    with _devnull('r') as fin, _devnull('w') as fout:
        code = subprocess.call([WOFF2_DECOMPRESS_PATH, input_path],
            stdin=fin, stdout=fout, stderr=fout)
        if code != 0:
            raise Error('conversion with woff2_decompress failed')
