
from html.parser import HTMLParser
from urllib import request
from urllib.error import HTTPError
from tkinter import *
from os.path import exists
from os import mkdir


class MangaPandaChecker(HTMLParser):
    """
    Current Usage:

    # first declare a MangaChecker
    checker = MangaPandaChecker()

    # next simply use the <check> method to get a list of
    # all chapters under that name
    # ex. for 'bleach'
    checker.check_for_update('bleach')

    # this will print a list of all chapters of bleach from MangaPanda

    # ex. for 'onepunch man'
    checker.check_for_update('onepunch man')
    # this will print a list of all chapters of onepunch man from MangaPanda
    """

    def __init__(self):
        super(MangaPandaChecker, self).__init__()
        self.chapter_listing_started = False
        self.chapter_found = False
        self.chapter_list = []

    def handle_starttag(self, tag, attrs):
        if self.chapter_listing_started:
            if tag == 'a':
                self.chapter_found = True
        if tag == 'div':
            if ('id', 'chapterlist') in attrs:
                self.chapter_listing_started = True
            elif ('class', 'clear') in attrs:
                self.chapter_listing_started = False

    def handle_endtag(self, tag):
        if self.chapter_listing_started:
            if tag == 'a':
                self.chapter_found = False

    def handle_data(self, data):
        if self.chapter_found:
            self.chapter_list.append(data)

    def check_for_update(self, manga):
        self.chapter_listing_started = False
        self.chapter_found = False
        self.chapter_list = []

        html = get_html(manga)

        if not html:
            return []

        self.feed(html)

        return sorted(self.chapter_list)


def get_old_listing(manga):
    try:
        file = open(manga + '.txt', 'r')
    except FileNotFoundError:
        return []

    return [chapter.strip() for chapter in file]


def get_html(manga):
    try:
        with request.urlopen('http://www.mangapanda.com/' +
                             '-'.join(manga.split(' '))) as response:
            html = str(response.read())
    except HTTPError:
        return None

    return html


def record(manga, chapter_list):
    if not exists('manga/'):
        mkdir('manga/')

    file = open('manga/' + manga + '.txt', 'w')
    for chapter in chapter_list:
        file.write(chapter + '\n')


def check(manga):
    checker = MangaPandaChecker()
    new_chapter_list = checker.check_for_update(manga)
    old_chapter_list = get_old_listing(manga)
    record(manga, new_chapter_list)
    difference = list(set(new_chapter_list) - set(old_chapter_list))

    chapters = sorted([int(chapter.split(' ')[-1]) for chapter in difference])

    title = manga.capitalize() + ' '
    return [title + str(chapter) for chapter in chapters]


def get_mangas():
    if not exists('manga.txt'):
        return []
    file = open('manga.txt', 'r')
    return [manga.strip() for manga in file]


def get_new_chapters():
    chapters = []
    for manga in get_mangas():
        for chapter in check(manga):
            chapters.append(chapter)

    return chapters


"""
Put all the manga names (from MangaPanda) in a file called manga.txt
one title per line (dont spell it wrong)

And this will print out all the new chapters in the console currently
as well as save the ones it just found in files in the folder manga
(which will be placed in the current directory)
"""

if __name__ == '__main__':
    for chapter in get_new_chapters():
        print(chapter)

