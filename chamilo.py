#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import requests
from BeautifulSoup import BeautifulSoup

from config import fix_folder_names, download_only

USERNAME = 'esi_id'
PASSWORD = 'esi_pass'
CHAMI_URL = 'https://elearning.esi.heb.be'
CHECK_SIZE = False
DOWNLOAD_ALL = False

s = requests.Session()

logging.basicConfig(filename='chamilo.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

log = logging.getLogger(__name__)


def authenticate(username, password):
    url = '%s/%s' % (CHAMI_URL, 'index.php')
    payload = {'login': username, 'password': password}

    return s.post(url, data=payload, verify=False)


def soup_content(url):
    return BeautifulSoup(s.get(url, verify=False).content)


def get_courses():
    if DOWNLOAD_ALL:
        url = '%s/%s' % (CHAMI_URL, 'main/auth/courses.php?action=display_courses&category_code=ALL&hidden_links=0')
        soup = soup_content(url)
        courses = [c for c in soup.findAll('a') if u'Accéder au cours' in c.text]
    else:
        url = '%s/%s' % (CHAMI_URL, 'user_portal.php')
        soup = soup_content(url)
        courses = [c.find('a') for c in soup.findAll('div', attrs={'class': 'well course-box'})]

    return courses


def download_course(course_info):
    url = course_info['href']
    name = url.split('/')[4]

    soup = soup_content(url)
    urls = soup.findAll('a', attrs={'target': '_self'})
    for url in urls:
        if 'Document' in url.text:
            url = url['href']
            break

    if 'document.php' in url:
        document_url = url
        soup = soup_content(url)

        folders = [x['value'] for x in soup.findAll('option')]
        for folder in folders:
            save_folders(name, folder)


def save_folders(name, number):
    url = '%s/main/document/document.php?id=%s&_qf__selector=&cidReq=%s' % (CHAMI_URL, number, name)
    soup = soup_content(url)

    soup = soup.find('table')
    if not soup:
        return

    prev_files = '' # XXX: some files appear twice or more
    for td in soup.findAll('tr'):
        if td.find('small'):
            files = td.find('a', attrs={'style': 'float:left'})
            date = td.find('small').text.split()[0]

            if files and files != prev_files and 'courses' in files.get('href'):
                url = files.get('href')
                save_file(name, url, date, CHECK_SIZE)

            prev_files = files


def save_file(path, url, date, check=False):
    name = '/'.join(url.split('/')[4:]).replace('document/', '')
    course_name = name.split('/')[0]
    name = name.replace(course_name, fix_folder_names.get(course_name))
    path = '/'.join(name.split('/')[:-1])

    if not os.path.exists(path):
        log.info('"%s" created' % (path))
        os.makedirs(path)

    name = '.'.join(name.split('.')[:-1]) + '-' + date + '.' + name.split('.')[-1] if '.' in name else name + '-' + date
    same_filesize = check_size(url, name) if check else True

    if not os.path.exists(name) or not same_filesize:
        with open(name, 'wb') as f:
            f.write(s.get(url, verify=False).content)
        log.info('"%s"... saved' % (name))


def check_size(url, name):
    chami_filesize = int(s.head(url, verify=False).headers['content-length'])
    local_filesize = os.path.getsize(name) if os.path.exists(name) else 0

    # ugly hack due to false content length for empty file
    if chami_filesize == 20:
        chami_filesize = 0

    return chami_filesize == local_filesize


if __name__ == '__main__':

    from sys import argv, exit, platform
    import ConfigParser
    import HTMLParser
    h = HTMLParser.HTMLParser()

    def _exit():
        if platform == 'win32':
            raw_input('Press Enter to close')
        exit()

    try:
        config = ConfigParser.RawConfigParser()
        config.read('credentials.ini')

        USERNAME = config.get('chamilo', 'username') if USERNAME == 'esi_id' else USERNAME
        PASSWORD = config.get('chamilo', 'password') if PASSWORD == 'esi_pass' else PASSWORD
    except:
        pass

    if USERNAME == 'esi_id' or PASSWORD == 'esi_pass':
        log.error('Please enter your credentials. Quitting.')
        _exit()

    if 'check' in argv:
        log.warn('Checking size while downloading (slower).')
        CHECK_SIZE = True

    auth = authenticate(USERNAME, PASSWORD)
    if 'user_password_incorrect' in auth.url:
        log.error('Could not login, check user & password.')
        _exit()

    if 'all' in argv:
        DOWNLOAD_ALL = True
        log.info('Download of all courses in progress.')

    if 'list-courses' in argv:
        DOWNLOAD_ALL = True

    log.info('Checking courses...')
    courses = get_courses()

    if download_only:
        courses = [c for c in courses if c['href'].split('/')[4] in download_only]

    if not courses:
        log.info('No courses found.')

    for course in courses:
        name = course['href'].split('/')[4]

        if 'list-courses' in argv:
            print(name + ' - ' + h.unescape(course.find('img')['alt']) if course.find('img') else '[none]')
            continue

        if 'update' in argv:
            if not 'Depuis votre dernière visite' in str(courses):
                log.info('Nothing to do.')
                break

            if 'Depuis votre dernière visite' in str(course):
                log.info('Updating files for %s' % name)
                download_course(course)

        else:
            log.info('Downloading files for %s' % name)
            download_course(course)

    _exit()
    # TODO: test on Windows if can be removed
    # if platform == 'win32':
    #     raw_input('Press Enter to close')

