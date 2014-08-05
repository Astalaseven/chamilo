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
	
then you can use it:

```
python chamilo.py
```	