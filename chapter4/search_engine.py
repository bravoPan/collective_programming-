from bs4 import BeautifulSoup
import requests
from pprint import pprint
from sqlite3 import dbapi2 as sqlite

class crawler:
    def __init__(self, dbname):
        self.con = sqlite.connect(dbname)
        pass

    def __del__(self):
        self.con.close()
        pass

    def db_commit(self):
        self.con.commit()
        pass

    def get_entry_id(self, table, field, value, create_new=True):
        return None

    def add_to_index(self, url, soup):
        print("Indexing{}".format(url))

    def get_text_only(self, soup):
        return None

    def separate_words(self, text):
        return None

    def is_indexed(self, url):
        return False

    def add_link_ref(self, url_from, url_to, link_text):
        pass

    def crawl(self, pages, depth=2):
        for i in range(depth):
            new_pages = set()
            for page in pages:
                try:
                    c = requests.get(page)
                except:
                    print("can not open{}".format(page))
                    continue
                soup = BeautifulSoup(c.text, "lxml")
                self.add_to_index(page, soup)

                links = soup("a")
                for link in links:
                    if "href" in dict(link.attrs):
                        next_href = link.get("href")
                        if "http" in next_href and not self.is_indexed(next_href):
                            next_href = next_href.split("#")[0]
                            new_pages.add(next_href)
                        link_text = self.get_text_only(link)
                        self.add_link_ref(page, next_href, link_text)
                self.db_commit()
        pass

    def create_index_tables(self):
        self.con.execute("CREATE TABLE urllist(url)")
        self.con.execute("CREATE TABLE wordlist(word)")
        self.con.execute("CREATE TABLE wordlocation(urlid, wordid, locationid)")
        self.con.execute("CREATE TABLE link(fromid INTEGER , toid INTEGER)")
        self.con.execute("CREATE TABLE linkwords(wordid, linkid)")
        self.con.execute("CREATE INDEX wordidx ON wordlist(word)")
        self.con.execute("CREATE INDEX urlidx ON urllist(url)")
        self.con.execute("CREATE INDEX wordurlidx ON wordlocation(wordid)")
        self.con.execute("CREATE INDEX urltoidx ON link(toid)")
        self.con.execute("CREATE INDEX urlfromidx ON link(fromid)")
        self.db_commit()
        pass


if __name__ == "__main__":
    page_list = ["https://zh.wikipedia.org/wiki/%E9%97%9C%E5%8E%9F%E4%B9%8B%E6%88%B0"]
    test = crawler("search_index.db")
    test.create_index_tables()
    # test.crawl(page_list)
