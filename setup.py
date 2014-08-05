from distutils.core import setup
import py2exe

to_exclude = ['_ssl', '_hashlib', 'doctest', 'difflib', 'pickle',
'ftp_lib', 'ssl', 'cmd', 'unittest']

setup(
    options = {'py2exe': {'bundle_files': 1, 'compressed': True, 'excludes': to_exclude, 'optimize': 2}},
    console = ['chamilo.py'],
    zipfile = None,
)
