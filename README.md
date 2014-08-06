chamilo
=======

Script to download all files from courses on Chamilo elearning platform.
Tested on http://elearning.esi.heb.be, Chamilo platform for [ESI](http://www.heb.be/esi/).

## Installation

```
pip install -r requirements # requests & BeautifulSoup
git clone https://github.com/Astalaseven/chamilo.git
```
	
## Usage

You first need to edit your credentials:

```
USERNAME = 'esi_id'
PASSWORD = 'esi_pass'
```
or into `credentials.ini`:
```
[chamilo]
username = esi_id
password = esi_pass
```

Then you can use it: `python chamilo.py`.

## Windows

A build is available in the `dist` folder.

You only have to put your credentials in `dist/credentials.ini` and double clic on `dist/chamilo`.

### Rebuilding on Windows

* Install [python2.7](https://www.python.org/ftp/python/2.7.8/python-2.7.8.msi)
and [py2exe](http://sourceforge.net/projects/py2exe/files/py2exe/0.6.9/py2exe-0.6.9.win32-py2.7.exe/download)
(direct links)
* `python setup.py py2exe`
* Download [UPX](http://sourceforge.net/p/upx/wiki/Home/)
* `upx --ultra-brute dist\chamilo.exe` to reduce the binary size (4.329 Ko -> 2.807 Ko, 64.83%)
