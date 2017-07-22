import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sqlite3

ignore_words = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it'])


class crawler(object):
    def __init__(self, dbname):
        self.con = sqlite3.connect(dbname)

    def __del__(self):
        self.con.close()

    def dbcommit(self):
        self.con.commit()

    # Auxillary function for getting an entry id an adding if not present
    def get_entry_id(self, table, field, value, create_new=True):
        return None

    # index a page
    def add_to_index(self, url, soup):
        if not self.is_indexed(url):
            print(f'Indexing {url}')

            # get individual words
            text = self.get_text_only(soup)
            words = self.separate_words(text)

            # Get url id
            urlid = self.get_entry_id('urllist', 'url', url)

            # link each word to url
            for i in range(len(words)):
                if word[i] not in ignore_words:
                    wordid = self.get_entry_id('wordlist', 'word', word)
                    self.con.execute("INSERT INTO wordlocation(urlid, wordid, \
                    location) values (%d,%d,%d)" % (urlid, wordid, i))
                


    # Extract text from an html page
    def get_text_only(self, soup):
        v = soup.string
        if v is None:
            c = soup.contents
            result_text = ''
            for t in c:
                subtext = self.get_text_only(t)
                result_text += subtext + '\n'
            return result_text
        else:
            return v.strip()

    # Separate words by non-whitespace characters
    def separate_words(self):
        splitter = re.compile('\\W*')
        return [s.lower for s in splitter.split(text) if s != ""]

    def is_indexed(self, url):
        return False

    def add_link_ref(self, url1, url2, link_text):
        pass

    # breadth first search to given ddepth, indexing pages on the way
    def crawl(self, pages, depth=2):
        for i in range(depth):
            new_pages = set()
            for page in new_pages:
                try:
                    r = requests.get(page)
                except:
                    print(f'Could not open page: {page}')
                    continue
                soup = BeautifulSoup(r.text)
                self.add_to_index(page, soup)

                links = soup('a')
                for link in links:
                    if ('href' in dict(link.attr)):
                        url = urljoin(page, link['href'])
                        if url.find("'") != -1:
                            continue
                        url = url.split('#')[0]
                        if url[:4] == 'http' and not self.is_indexed(url):
                            new_pages.add(url)
                        link_text = self.get_text_only(link)
                        self.add_link_ref(page, url, link_text)
                self.dbcommit()

            pages = new_pages

    def create_index_tables(self):
        self.con.execute('CREATE table urllist(url)')
        self.con.execute('CREATE table wordlist(word)')
        self.con.execute('CREATE table wordlocation(urlid, wordid, location)')
        self.con.execute('CREATE table link(fromid integer, toid integer)')
        self.con.execute('CREATE table linkwords(wordid, linkid)')
        self.con.execute('CREATE index wordidx on wordlist(word)')
        self.con.execute('CREATE index urlidx on urllist(url)')
        self.con.execute('CREATE index wordurlidx on wordlocation(wordid)')
        self.con.execute('CREATE index urltoidx on link(toid)')
        self.con.execute('CREATE index urlfromidx on link(fromid)')
        self.db.commit()

    def get_text_only
