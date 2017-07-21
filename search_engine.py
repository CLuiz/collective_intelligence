class crawler(object):
    def __init__(self, dbname):
        pass

    def __del__(self):
        pass

    def dbcommit(self):
        pass

    # Auxillary function for getting an entry id an adding if not present
    def get_entry_id(self, table, field, value, create_new=True):
        return None

    # index a page
    def add_to_index(self, url, soup):
        print(f'Indexing {url}')

    # Extract text from an html page
    def get_text_only(self, soup):
        return None

    # Separate words by non-whitespace characters
    def separate_words(self):
        return None

    def is_indexed(self, url):
        return False

    def add_link_ref(self, url1, url2, link_text):
        pass

    # breadth first search to given ddepth, indexing pages on the way
    def crawl(self, pages, depth=2):
        pass

    def create_index_tabels(db):
        pass
