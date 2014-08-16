#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import requests
from BeautifulSoup import BeautifulSoup

USERNAME = 'esi_id'
PASSWORD = 'esi_pass'
CHAMI_URL = 'https://elearning.esi.heb.be'
CHECK_SIZE = False

s = requests.Session()


def authenticate(username, password):
    url = '%s/%s' % (CHAMI_URL, 'index.php')
    payload = {'login': username, 'password': password}

    return s.post(url, data=payload, verify=False)


def soup_content(url):
    return BeautifulSoup(s.get(url, verify=False).content)


def get_courses():
    url = '%s/%s' % (CHAMI_URL, 'user_portal.php')

    soup = soup_content(url)
    courses = soup.findAll('div', attrs={'class': 'userportal-course-item'})

    return courses


def download_course(course_info):
    url = course_info.find('a')['href']
    name = url.split('/')[4]

    soup = soup_content(url)
    url = soup.find('a', attrs={'title': 'Documents'})
    if url:
        document_url = '%s%s' % (CHAMI_URL, url['href'])
        soup = BeautifulSoup(s.get(document_url, verify=False).content)

        folders = [x['value'] for x in soup.findAll('option')]
        for folder in folders:
            save_folders(name, folder)


def save_folders(name, url):
    url = '%s/main/document/document.php?cidReq=%s&curdirpath=%s' % (CHAMI_URL, name, url)
    soup = soup_content(url)

    files = soup.findAll('a', attrs={'style': 'float:right'})
    for file in files:
        url = '%s%s' % (CHAMI_URL, file['href'])
        save_file(name, url)


def save_file(path, url, check=CHECK_SIZE):
    name = '/'.join(url.split('%2F')[1:])
    name = '%s/%s' % (path, name)
    path = '/'.join(name.split('/')[:-1])

    if not os.path.exists(path):
        print('"%s" created' % (path))
        os.makedirs(path)

    same_filesize = check_size(url, name) if check else True

    if not os.path.exists(name) or not same_filesize:
        print('"%s"...' % (name)),
        with open(name, 'wb') as f:
            f.write(s.get(url, verify=False).content)
        print(' saved')


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

    try:
        config = ConfigParser.RawConfigParser()
        config.read('credentials.ini')

        USERNAME = config.get('chamilo', 'username') if USERNAME == 'esi_id' else USERNAME
        PASSWORD = config.get('chamilo', 'password') if PASSWORD == 'esi_pass' else PASSWORD
    except:
        pass

    if USERNAME == 'esi_id' or PASSWORD == 'esi_pass':
        print('Please enter your credentials. Quitting.')
        if platform == 'win32':
            raw_input('Press Enter to close')
        exit()
        
    if 'check' in argv:
        print('Checking size while downloading (slower)')
        CHECK_SIZE = True

    auth = authenticate(USERNAME, PASSWORD)
    if 'user_password_incorrect' in auth.url:
        print('Could not login, check user & password')
        if platform == 'win32':
            raw_input('Press Enter to close')
        exit()

    print('Checking courses...')
    courses = get_courses()
 
    for course in courses:
        name = course.find('a')['href'].split('/')[4]
        
        if 'update' in argv:
            if '-- Documents --' in str(course):
                print('Updating files for %s' % name)
                download_course(course)

        else:
            print('Downloading files for %s' % name)
            download_course(course)

    if platform == 'win32':
        raw_input('Press Enter to close')
 