from html.parser import HTMLParser
from urllib import request
from urllib.error import HTTPError
from os.path import exists
from os import mkdir


# from http://stackoverflow.com/questions/5967500/
#          how-to-correctly-sort-a-string-with-a-number-inside

import re


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    """
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    """
    return [ atoi(c) for c in re.split('(\d+)', text) ]


class MangaSite(HTMLParser):
    """An abstract class that will allow you to extract all the released
    chapters of a manga on a certain site.

    """

    def __init__(self, url, separator):
        super(MangaSite, self).__init__()
        self.chapter_lists_started = False
        self.chapter_found = False
        self.chapter_list = set()
        self.url = url
        self.separator = separator

    def handle_starttag(self, tag, attrs):
        if self.chapter_lists_started:
            if self.was_chapter_found(tag, attrs):
                self.chapter_found = True
        if self.has_chapter_lists_started(tag, attrs):
            self.chapter_lists_started = True
        elif self.has_chapter_lists_ended(tag, attrs):
            self.chapter_lists_started = False

    def handle_endtag(self, tag):
        if self.chapter_lists_started:
            if self.has_chapter_ended(tag):
                self.chapter_found = False

    def handle_data(self, data):
        if self.chapter_found:
            self.chapter_list.add(data.split(' ')[-1])

    def has_chapter_lists_started(self, tag, attrs):
        """

        :param tag: the tag found
        :type tag: str
        :param attrs: the attributes of the tag
        :type attrs: str
        :return: if this tag signals a chapter list has started
        :rtype: bool
        """
        raise NotImplementedError

    def has_chapter_lists_ended(self, tag, attrs):
        """

        :param tag: the tag found
        :type tag: str
        :param attrs: the attributes of the tag
        :type attrs: str
        :return: if this tag signals a chapter list has ended
        :rtype: bool
        """
        raise NotImplementedError

    def was_chapter_found(self, tag, attrs):
        """

        :param tag: the tag found
        :type tag: str
        :param attrs: the attributes of the tag
        :type attrs: str
        :return: if this tag signals a chapter has been found
        :rtype: bool
        """
        raise NotImplementedError

    def has_chapter_ended(self, tag):
        """

        :param tag: the tag found
        :type tag: str
        :return: if this tag signals a chapter has ended
        :rtype: bool
        """
        raise NotImplementedError

    def check_for_updates(self, manga):
        """

        :param manga: the manga to check for
        :type manga: str
        :return: a set of all chapters of this manga
        :rtype: set{str}
        """
        manga = manga.lower()
        self.chapter_lists_started = False
        self.chapter_found = False
        self.chapter_list = set()

        html = self.get_html(manga)

        if html is None:
            return []

        self.feed(html)

        return self.chapter_list

    def get_html(self, manga):
        """

        :param manga: the name of the manga
        :type manga: str
        :return: the html of the webpage for this manga on this site
        :rtype: str
        """
        try:
            with request.urlopen(self.url +
                                 self.separator.join(manga.split(' ')))\
                    as response:
                html = str(response.read())
        except HTTPError:
            return None
        return html


class MangaPanda(MangaSite):

    def __init__(self):
        super(MangaPanda, self).__init__('http://www.mangapanda.com/', '-')

    def has_chapter_lists_started(self, tag, attrs):
        return tag == 'table' and ('id', 'listing') in attrs

    def has_chapter_lists_ended(self, tag, attrs):
        return tag == 'table'

    def was_chapter_found(self, tag, attrs):
        return tag == 'a'

    def has_chapter_ended(self, tag):
        return tag == 'a'


class MangaFox(MangaSite):

    def __init__(self):
        super(MangaFox, self).__init__('http://www.mangafox.me/manga/', '_')

    def has_chapter_lists_started(self, tag, attrs):
        return tag == 'ul' and ('class', 'chlist') in attrs

    def has_chapter_lists_ended(self, tag, attrs):
        return tag == 'ul'

    def was_chapter_found(self, tag, attrs):
        return tag == 'a' and ('class', 'tips') in attrs

    def has_chapter_ended(self, tag):
        return tag == 'a'


def get_mangas(src='manga.txt'):
    """Return a list of the mangas to check for

    :param src: file containing all the mangas
    :type src: str
    :return: list of all the manga titles in the file (and alternate titles)
    :rtype: list[list[str]]
    """

    """
            ^^         |         ^^
            ::         |         ::
     ^^     ::         |         ::     ^^
     ::     ::         |         ::     ::
      ::     ::        |        ::     ::
        ::    ::       |       ::    ::
          ::    ::   _/~\_   ::    ::
            ::   :::/     \:::   ::
              :::::(       ):::::
                    \ ___ /
               :::::/`   `\:::::
             ::    ::\o o/::    ::
           ::     ::  :":  ::     ::
         ::      ::   ` `   ::      ::
        ::      ::           ::      ::
       ::      ::             ::      ::  R. Nykvist (Chuckles)
       ^^      ::             ::      ^^
               ::             ::
               ^^             ^^
    """
    if not exists(src):  # Fail silently XD
        return []

    file = open(src, 'r')
    return [manga.strip().split('$$') for manga in file]


def get_old_listings(mangas=get_mangas(), src='manga/'):
    """

    :param mangas: the manga titles
    :type mangas: list[lst[str]]
    :param src: path to listing
    :type src: str
    :return: dictionary mapping manga title to its logged chapters
    :rtype: dict{str: set{str}}
    """
    '''
               ;               ,
             ,;                 '.
            ;:                   :;
           ::                     ::
           ::                     ::
           ':                     :
            :.                    :
         ;' ::                   ::  '
        .'  ';                   ;'  '.
       ::    :;                 ;:    ::
       ;      :;.             ,;:     ::
       :;      :;:           ,;"      ::
       ::.      ':;  ..,.;  ;:'     ,.;:
        "'"...   '::,::::: ;:   .;.;""'
            '"""....;:::::;,;.;"""
        .:::.....'"':::::::'",...;::::;.
       ;:' '""'"";.,;:::::;.'""""""  ':;
      ::'         ;::;:::;::..         :;
     ::         ,;:::::::::::;:..       ::
     ;'     ,;;:;::::::::::::::;";..    ':.
    ::     ;:"  ::::::"""'::::::  ":     ::
     :.    ::   ::::::;  :::::::   :     ;
      ;    ::   :::::::  :::::::   :    ;
       '   ::   ::::::....:::::'  ,:   '
        '  ::    :::::::::::::"   ::
           ::     ':::::::::"'    ::
           ':       """""""'      ::
            ::                   ;:
            ':;                 ;:"
    -hrr-     ';              ,;'
                "'           '"
                  '
    '''
    old_listings = {}
    for manga_titles in mangas:
        listing = set()

        if exists(src + manga_titles[0] + '.txt'):  # Again, Fail silently XD
            file = open(src + manga_titles[0] + '.txt', 'r')

            for chapter in file:
                listing.add(chapter.strip().title())
        old_listings[manga_titles[0]] = listing
    return old_listings


def build_new_listings(srcs, mangas=get_mangas()):
    """

    :param srcs: list of sites as sources
    :type srcs: list[MangaSite]
    :param mangas: list of manga titles
    :type mangas: list[str]
    :return: dictionary mapping manga title to its chapters
    :rtype: dict{str: set{str}}
    """
    new_listings = {}
    for manga_titles in mangas:
        listing = set()
        for manga in manga_titles:
            for src in srcs:
                listing = listing.union(src.check_for_updates(manga))
        new_listings[manga_titles[0]] = listing
    return new_listings


def change_in_listings(old, new, mangas=get_mangas()):
    change = {}

    for manga_title in mangas:
        change[manga_title[0]] = new[manga_title[0]] - old[manga_title[0]]

    return change


def log_listings(listings, src='manga/'):
    """

    :param listings: dictionary mapping manga title to its chapters
    :type listings: dict{str: list[str]}
    :param src: folder to place the logs in
    :type src: str
    """
    if not exists(src):
        mkdir(src)

    for manga, chapters in listings.items():
        file = open(src + manga + '.txt', 'w')
        for chapter in sorted(chapters, key=natural_keys):
            file.write(chapter)
            file.write('\n')
