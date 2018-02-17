import re
import math
from sqlite3 import dbapi2 as sqlite


def sample_train(c1):
    c1.train("Nobody owns the water.", "good")
    c1.train("the quick rabbit jumps fences", "good")
    c1.train("but pharmaceuticals now", "bad")
    c1.train("make quick money at the online casino", "bad")
    c1.train("the quick brown fox jumps", "good")


def get_words(doc):
    splitter = re.compile("\\W*")
    words = [s.lower() for s in splitter.split(doc) if 2 < len(s) < 20]
    return dict([(w, 1) for w in words])


class classifier:
    def __init__(self, get_features, filename=None):
        # 统计特征/分类组合的数量
        self.fc = {}
        # 每个文档中的文档数量
        self.cc = {}
        self.get_features = get_features
        self.thresholds = {}

    def set_db(self, db_file="test1.db"):
        self.con = sqlite.connect(db_file)
        self.con.execute("CREATE TABLE IF NOT EXISTS fc(feature, category, count)")
        self.con.execute("CREATE TABLE IF NOT EXISTS cc(category, count)")

    def set_threshold(self, cat, t):
        self.thresholds[cat] = t

    def get_threshold(self, cat):
        if cat not in self.thresholds:
            return 1.0
        return self.thresholds[cat]

    def classify(self, item, default=None):
        probs = {}
        max = 0.0
        for cat in self.categories():
            probs[cat] = self.f_prob(item, cat)
            max = probs[cat]
            best = cat

        # 确保概率值超过值域 * 次大概率值
        for cat in probs:
            if cat == best:
                continue
            if probs[cat] * self.get_threshold(best) > probs[best]:
                return default

        return best

    # 增加对特征/分类组合的计数值
    def inc_f(self, f, cat):
        count = self.f_count(f, cat)
        if count == 0:
            self.con.execute("INSERT INTO fc VALUES ('%s', '%s', 1)" % (f, cat))
        else:
            self.con.execute("UPDATE fc SET count=%d WHERE feature='%s' and category='%s'" % (count + 1, f, cat))

    # 增加对某一分类的计数值
    def incc(self, cat):
        count = self.cat_count(cat)
        if count == 0:
            self.con.execute("INSERT INTO cc VALUES ('%s', 1)" % cat)
        else:
            self.con.execute("UPDATE cc SET count=%d WHERE category='%s'" % (count + 1, cat))

    # 某一特征出现于某一分类的次数
    def f_count(self, f, cat):
        res = self.con.execute('SELECT count FROM fc WHERE feature="%s" and category="%s"' % (f, cat)).fetchone()
        if not res:
            return 0
        else:
            return float(res[0])

    # 属于某一分类的内容数量
    def cat_count(self, cat):
        res = self.con.execute('SELECT count FROM cc WHERE category="%s" ' % cat).fetchone()
        if not res:
            return 0
        else:
            return float(res[0])

    # 所有内容的数量
    def total_count(self):
        res = self.con.execute("SELECT sum(count) FROM cc").fetchone()
        if not res:
            return 0
        return res[0]

    # 所有内容的分类
    def categories(self):
        cur = self.con.execute("SELECT category FROM cc")
        return [d[0] for d in cur]

    def train(self, item, cat):
        features = self.get_features(item)
        for f in features:
            self.inc_f(f, cat)
        self.incc(cat)
        self.con.commit()

    def f_prob(self, f, cat):
        if self.cat_count(cat) == 0:
            return 0
        # 特征在分类中出现的总次数，除以分类中包含内容项的总次数
        return self.f_count(f, cat) / self.cat_count(cat)

    def weighted_prob(self, f, cat, prf, weight=1.0, ap=0.5):
        basic_prob = prf(f, cat)
        totals = sum([self.f_count(f, c) for c in self.categories()])
        bp = ((weight * ap) + (totals * basic_prob)) / (weight + totals)
        return bp


class NaiveBayes(classifier):
    #  将item中的所有单词乘以特征得到整篇文章的概率
    def doc_prob(self, item, cat):
        features = self.get_features(item)

        p = 1
        for f in features:
            p *= self.weighted_prob(f, cat, self.f_prob)
        return p

    # 朴素贝叶斯过滤器, Pr(Category|Document) = Pr(Document|Category) * Pr(Category) / Pr(Document),
    # Pr(Category),就是该分类的文档数除以文档总数
    # Pr(Document)代表随意挑选一篇文章属于该分类的概率
    def prob(self, item, cat):
        # Pr(Category)
        cat_prob = self.cat_count(cat) / self.total_count()
        doc_prob = self.doc_prob(item, cat)
        return doc_prob * cat_prob


class FisherClassifier(classifier):
    def __init__(self, get_features):
        classifier.__init__(self, get_features)
        self.minimums = {}

    def set_minimum(self, cat, min):
        self.minimums[cat] = min

    def get_minimum(self, cat):
        if cat not in self.minimums:
            return 0
        return self.minimums[cat]

    def classify(self, item, default=None):
        best = default
        max_value = 0.0
        for c in self.categories():
            p = self.fisher_prob(item, c)
            if p > self.get_minimum(c) and p > max_value:
                best = c
                max_value = p
        return best

    def c_prob(self, f, cat):
        clf = self.f_prob(f, cat)
        if clf == 0:
            return 0
        freq_sum = sum([self.f_prob(f, c) for c in self.categories()])
        p = clf / freq_sum
        return p

    def invhi2(self, chi, df):
        m = chi / 2.0
        sum = term = math.exp(-m)
        for i in range(1, df // 2):
            term *= m / i
            sum += term
        return min(sum, 1.0)

    def fisher_prob(self, item, cat):
        p = 1
        features = self.get_features(item)
        for f in features:
            p *= (self.weighted_prob(f, cat, self.c_prob))
        f_score = -2 * math.log(p)
        return self.invhi2(f_score, len(features) * 2)


if __name__ == "__main__":
    test_sentence = "Hi there, May  be you do not know me. But this is True"
    good_one = "Hi Pan, We are welcomed you are admitted!"
    # get_words(test_sentence)
    c1 = FisherClassifier(get_words)
    # c1.train(test_sentence, "bad")
    # c1.train(good_one, "good")
    # print(c1.f_count("pan", "good"))
    # print(c1.f_count("you", "bad"))
    c1.set_db("test1.db")
    # sample_train(c1)
    c12 = NaiveBayes(get_words)
    c12.set_db("test1.db")
    print(c12.classify("quick money"))
    # c1.train(c1)

    # c1.set_db("test1.db")
    # for i in range(1000):
    #     sample_train(c1)
    # print(c1.classify("quick rabbit"))
    # print(c1.classify("quick money"))
    # c1.set_minimum("bad", 0.8)
    # print(c1.classify("quick money"))
