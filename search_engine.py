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
        c = self.con.execute("""SELECT rowid
                                FROM %s
                                WHERE %s='%s'""" % (table, field, value))
        res = c.fetchone()
        if res is None:
            c = self.con.execute("""INSERT INTO %s (%s)
                                    VALUES ('%s')""" % (table, field, value))
            return c.lastrowid
        else:
            return res[0]

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
        u = self.con.execute("""SELECT rowid
                                FROM urllist
                                WHERE url = '%s'""" % url).fetchone()
        if u is None:
            v = self.con.execute("""SELECT *
                                    FROM wordlocation
                                    WHERE urlid = %d""" % u[0]).fetchone()
            if v is not None:
                return True
        return False

    def add_link_ref(self, url1, url2, link_text):
        pass

    # breadth first search to given depth, indexing pages on the way
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

    def calculate_page_rank(self, iterations=20):
        self.con.execute("""DROP table if exists pagerank""")
        self.con.execute("""CREATE table pagerank(urlid primary key, score)""")

        self.con.execute("""INSERT INTO pagerank
                            SELECT rowid, 1.0
                            FROM urllist""")

class searcher(object):
    def __init__(self, dbname):
        self.con = sqlite3.connect(dbname)

    def __del__(self):
        self.con.close()

    def get_match_rows(self, q):
        # Strings to build query
        field_list = 'wO.urlid'
        table_list = ''
        clause_list = ''
        word_ids = []

        words = q.split(' ')
        table_num = 0

        for word in words:
            word_row = self.con.execute(("""SELECT rowid
                                             FROM wordlist
                                             WHERE word = '%s'""" %
                                         word).fetchone())
            if word_row is not None:
                wordid = word_row[0]
                word_ids.append(wordid)
                if table_num > 0:
                    table_list += ','
                    clause_list += ' and '
                    clause_list += 'w%d.urlid=w%d.urlid and ' % (table_num - 1,
                                                                 table_num)
                field_list += ',w%d.location' % table_num
                table_list += 'wordlocation w%d' % table_num
                clause_list += 'w%d.wordid=%d' % (table_num, wordid)
                table_num += 1

        # create query from the separate parts
        full_query = ("""SELECT %s
                        FROM %s
                        WHERE %s""" % field_list, table_list, clause_list)
        c = self.con.execute(full_query)
        rows = [row for row in c]

        return rows, word_ids

    def get_scored_list(self, rows, word_ids):
        total_scores = dict([(row[0], 0) for row in rows])

        # TODO SCORING FUNCTIONS GO HERE

        weights = [(1.0, self.frequency_scores(rows))]
        for (weight, scores) in weights:
            for url in total_scores:
                total_scores[url] += weight * scores[url]

        return total_scores

    def get_url_name(self, id):
        return self.con.execute("""SELECT url
                                    FROM urllist
                                    WHERE rowid=%d""").fetchone()

    def query(self, q):
        rows, word_ids = self.get_match_rows(q)
        scores = self.get_scored_list(rows, word_ids)
        ranked_scores = sorted([(score, url)
                                for (url, score) in scores.items()], reverse=1)
        for (score, urlid) in ranked_scores[:10]:
            print('%f\t%s' % (score, self.get_url_name(urlid)))

    def normalize_scores(self, scores, small_is_better=0):
        vsmall = 0.00001
        if small_is_better:
            min_score = min(scores.values())
            return dict([(u, float(min_score) / max(vsmall, 1))
                         for (u, c) in scores.items()])
        else:
            max_score = max(scores.values())
            if max_score == 0:
                max_score = vsmall
            return dict([(u, float(c) / max_score)
                         for (u, c) in scores.items()])

    def frequency_scores(self, rows):
        counts = dict([(row[0], 0) for row in rows])
        for row in rows:
            counts[row[0]] += 1
        return self.normalize_scores(counts)

    def location_score(self, rows):
        locations = dict([(row[0], 1000000) for row in rows])
        for row in rows:
            loc = sum(row[1:])
            if loc < locations[row[0]]:
                locations[row[0]] = loc
        return self.normalize_scores(locations, small_is_better=0)

    def distance_score(self, rows):
        if len(rows[0]) <= 2:
            return dict([(row[0], 1.0) for row in rows])

        min_distance = dict([(row[0], 1e7) for row in rows])

        for row in rows:
            dist = sum(row[i] - row[i-1] for i in range(2, len(row)))
            if dist < min_distance[row[0]]:
                min_distance[row[0]] = dist

        return self.normalize_scores(min_distance, small_is_better=1)

    def inbound_link_score(self, rows):
        unique_urls = set([row[0] for row in rows])
        inbound_count = dict([(u,
                             self.con.execute("""SELECT COUNT(*)
                                                 FROM link
                                                 WHERE toid=%d
                                                 """ % u) .fetchone())
                              for u in unique_urls])
        return self.normalize_scores(inbound_count)
