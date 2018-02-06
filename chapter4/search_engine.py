from bs4 import BeautifulSoup
import requests
from pprint import pprint
from sqlite3 import dbapi2 as sqlite
import re
from chapter4.config import ignored_words


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
        cur = self.con.execute("SELECT rowid FROM %s WHERE %s='%s'" % (table, field, value))
        res = cur.fetchone()
        if res == None:
            cur = self.con.execute("INSERT INTO %s (%s) VALUES ('%s')" % (table, field, value))
            return cur.lastrowid
        else:
            return res[0]

    def add_to_index(self, url, soup):
        if self.is_indexed(url):
            return
        print("Indexing{}".format(url))

        # get every word
        text = self.get_text_only(soup)
        words = self.separate_words(text)

        # get id of URL
        url_id = self.get_entry_id("urllist", "url", url)

        # link every word to word
        for i in range(len(words)):
            word = words[i]
            if word in ignored_words:
                continue
            word_id = self.get_entry_id("wordlist", "word", word)
            self.con.execute(
                "INSERT INTO wordlocation(urlid, wordid, locationid) VALUES ({}, {},{})".format(url_id, word_id, i))

    def get_text_only(self, soup):
        v = soup.string
        if v == None:
            c = soup.contents
            result_text = ''
            for t in c:
                sub_text = self.get_text_only(t)
                result_text += sub_text + "\n"
            return result_text
        else:
            return v.strip()

    def separate_words(self, text):
        splitter = re.compile("\\W+")
        return [s.lower() for s in splitter.split(text) if s != ""]

    def is_indexed(self, url):
        u = self.con.execute("SELECT rowid FROM urllist WHERE url='%s'" % url).fetchone()
        if u:
            v = self.con.execute("SELECT * FROM wordlocation WHERE urlid=%d" % u[0]).fetchone()
            if v:
                return True
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
    test = crawler("search_index.db")
    # test.create_index_tables()
    # pages = ["https://gl.wikipedia.org/wiki/Batalla_de_Sekigahara"]
    # test.crawl(pages)
    pprint([row for row in test.con.execute("SELECT * FROM wordlocation WHERE wordid=7")])
