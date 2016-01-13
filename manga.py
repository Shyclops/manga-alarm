
from html.parser import HTMLParser
from urllib import request
from urllib.error import HTTPError


class MangaPandaChecker(HTMLParser):
    """
    Current Usage:

    # first declare a MangaChecker
    checker = MangaChecker()

    # next simply use the <check> method to get a list of
    # all chapters under that name
    # ex. for 'bleach'
    checker.check('bleach')

    # this will print a list of all chapters of bleach from MangaPanda

    # ex. for 'onepunch man'
    checker.check('onepunch man')
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

    def check(self, manga):
        self.chapter_listing_started = False
        self.chapter_found = False
        self.chapter_list = []

        try:
            with request.urlopen('http://www.mangapanda.com/' +
                                 '-'.join(manga.split(' '))) as response:
                html = str(response.read())
        except HTTPError:
            print('Error looking for manga: ' + manga)
            return

        self.feed(html)

        return self.chapter_list
