from bs4 import BeautifulSoup
import requests
from pprint import pprint
from sqlite3 import dbapi2 as sqlite
import re
from chapter4.config import ignored_words
import time


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
        print("Indexing {}".format(url))

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
            pages = new_pages

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


class Searcher:
    def __init__(self, dbname):
        self.con = sqlite.connect(dbname)

    def __del__(self):
        self.con.close()

    def get_match_rows(self, q):
        field_list = "w0.urlid"
        table_list = ""
        clause_list = ""
        word_ids = []

        words = q.split(" ")
        table_number = 0

        for word in words:
            word_row = self.con.execute("SELECT rowid FROM wordlist WHERE word='%s'" % word).fetchone()
            if word_row:
                word_id = word_row[0]
                word_ids.append(word_id)
                if table_number > 0:
                    table_list += ","
                    clause_list += " and "
                    clause_list += "w%d.urlid=w%d.urlid and " % (table_number - 1, table_number)
                field_list += ",w%d.locationid" % table_number
                table_list += "wordlocation w%d" % table_number
                clause_list += "w%d.wordid=%d" % (table_number, word_id)
                table_number += 1

        full_query = "SELECT %s FROM %s WHERE %s" % (field_list, table_list, clause_list)
        cur = self.con.execute(full_query)
        rows = [row for row in cur]
        return rows, word_ids

    def get_scored_list(self, rows):
        total_scores = dict([(row[0], 0) for row in rows])

        weights = [[(1.0, self.location_score(rows))], [(1.0, self.frequency_score(rows))]]

        for (weight, scores) in weights[0]:
            for url in total_scores:
                total_scores[url] += weight * scores[url]

        return total_scores

    def get_url_name(self, id):
        return self.con.execute("SELECT url FROM urllist WHERE rowid=%d" % id).fetchone()[0]

    def query(self, q):
        rows, word_ids = self.get_match_rows(q)
        # pprint(rows)
        scores = self.get_scored_list(rows)

        ranked_score = sorted([(score, url) for (url, score) in scores.items()], reverse=True)
        # pprint(ranked_score)
        for (score, urlid) in ranked_score[0:10]:
            print("%f\t%s" % (score, self.get_url_name(urlid)))

    def normalize_scores(self, scores, small_is_better=0):
        v_small = 0
        if small_is_better:
            min_score = min(scores.values())
            inter_mediate_list = [(u, float(min_score) / max(v_small, j)) for (u, j) in scores.items()]
            return dict(inter_mediate_list)
        else:
            max_score = max(scores.values())
            if max_score == 0:
                max_score = v_small
            return dict([(u, float(c) / max_score) for (u, c) in scores.items()])

    # 根据单词频率划分权重
    def frequency_score(self, rows):
        counts = dict([row[0], 0] for row in rows)
        for row in rows:
            counts[row[0]] += 1
        return self.normalize_scores(counts)

    # 根据文档位置划分权重
    def location_score(self, rows):
        locations = dict([(row[0], 1000000) for row in rows])
        for row in rows:
            loc = sum(row[1:])
            if loc < locations[row[0]]:
                locations[row[0]] = loc
        return self.normalize_scores(locations, small_is_better=1)


if __name__ == "__main__":
    test = crawler("search_index.db")
    # test.create_index_tables()
    # pages = ["https://www.wikihow.com/Learn-English"]
    # test.crawl(pages, depth=2)
    # pprint([row for row in test.con.execute("SELECT * FROM urllist")])
    e = Searcher("search_index.db")
    e.query("samurai")
    # pprint(e.get_match_rows("dynamic programming"))
