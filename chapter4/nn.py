from math import tanh
from sqlite3 import dbapi2 as sqlite
from pprint import pprint

class SearchNet:
    def __init__(self, db_name):
        self.con = sqlite.connect(db_name)

    def __del__(self):
        self.con.close()

    def make_table(self):
        self.con.execute("CREATE TABLE hiddennode(create_key)")
        self.con.execute("CREATE TABLE wordhidden(fromid, toid, strength)")
        self.con.execute("CREATE TABLE hiddenurl(fromid, toid, strength)")
        self.con.commit()

    def get_strength(self, from_id, to_id, layer):
        if layer == 0:
            table = "wordhidden"
        else:
            table = "hiddenurl"
        res = \
            self.con.execute(
                "SELECT strength FROM %s WHERE fromid=%d AND toid=%d" % (table, from_id, to_id)).fetchone()
        if res == None:
            if layer == 0:
                return -0.2
            if layer == 1:
                return 0
        return res[0]

    def set_strength(self, from_id, to_id, layer, strength):
        if layer == 0:
            table = "wordhidden"
        else:
            table = "hiddenurl"
        res = self.con.execute("SELECT rowid FROM %s WHERE fromid=%d AND toid=%d" % (table, from_id, to_id)).fetchone()
        if res == None:
            self.con.execute(
                "INSERT INTO %s (fromid, toid, strength) VALUES  (%d, %d, %f)" % (table, from_id, to_id, strength))
        else:
            row_id = res[0]
            self.con.execute("UPDATE %s SET strength=%f WHERE rowid=%d" % (table, strength, row_id))

    def generate_hidden_node(self, word_ids, urls):
        if len(word_ids) > 3:
            return None
        create_key = "_".join(sorted([str(wi) for wi in word_ids]))
        res = self.con.execute("SELECT rowid FROM hiddennode WHERE create_key='%s'" % create_key).fetchone()

        if not res:
            cur = self.con.execute("INSERT INTO hiddennode (create_key) VALUES ('%s')" % create_key)
            hidden_id = cur.lastrowid
            for word_id in word_ids:
                self.set_strength(word_id, hidden_id, 0, 1.0 / len(word_ids))
            for url_id in urls:
                self.set_strength(hidden_id, url_id, 1, 0.1)
            self.con.commit()

    def get_all_hidden_ids(self, word_ids, url_ids):
        l1 = {}
        for word_id in word_ids:
            cur = self.con.execute("SELECT toid FROM wordhidden WHERE fromid=%d" % word_id)
            for row in cur:
                l1[row[0]] = 1
        for url_id in url_ids:
            cur = self.con.execute("SELECT fromid FROM hiddenurl WHERE toid=%d" % url_id)
            for row in cur:
                l1[row[0]] = 1
        return l1.keys()

    def set_up_net_work(self, word_ids, url_ids):
        self.word_ids = word_ids
        self.hidden_ids = self.get_all_hidden_ids(word_ids, url_ids)
        self.url_ids = url_ids

        self.ai = [1.0] * len(self.word_ids)
        self.ah = [1.0] * len(self.hidden_ids)
        self.ao = [1.0] * len(self.url_ids)

        self.wi = [[self.get_strength(word_id, hidden_id, 0)
                    for hidden_id in self.hidden_ids]
                   for word_id in self.word_ids]
        self.wo = [[self.get_strength(hidden_id, url_id, 1)
                    for url_id in self.url_ids]
                   for hidden_id in self.hidden_ids]

    def feed_forward(self):
        for i in range(len(self.word_ids)):
            self.ai[i] = 1.0

        for j in range(len(self.hidden_ids)):
            sum = 0.0
            for i in range(len(self.word_ids)):
                sum = sum + self.ai[i] * self.wi[i][j]
            self.ah[j] = tanh(sum)

        for k in range(len(self.url_ids)):
            sum = 0.0
            for j in range(len(self.hidden_ids)):
                sum = sum + self.ah[j] * self.wo[j][k]
                self.ao[k] = tanh(sum)

        return self.ao[:]

    def get_result(self, word_ids, url_ids):
        self.set_up_net_work(word_ids, url_ids)
        return self.feed_forward()


if __name__ == "__main__":
    my_net = SearchNet("nn.db")
    # my_net.make_table()
    w_word, w_river, w_bank = 101, 102, 103
    u_world_bank, u_river, u_earth = 201, 202, 203
    my_net.generate_hidden_node([w_word, w_bank], [u_world_bank, u_river, u_earth])
    # [print(c) for c in my_net.con.execute("SELECT * FROM wordhidden")]
    # [print(c) for c in my_net.con.execute("SELECT * FROM hiddenurl")]
    pprint(my_net.get_result([w_word, w_bank], [u_world_bank, u_river, u_earth]))
