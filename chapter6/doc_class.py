import re
import math


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

    # 增加对特征/分类组合的计数值
    def inc_f(self, f, cat):
        self.fc.setdefault(f, {})
        self.fc[f].setdefault(cat, 0)
        self.fc[f][cat] += 1

    # 增加对某一分类的计数值
    def incc(self, cat):
        self.cc.setdefault(cat, 0)
        self.cc[cat] += 1

    # 某一特征出现于某一分类的次数
    def f_count(self, f, cat):
        if f in self.fc and cat in self.fc[f]:
            return float(self.fc[f][cat])
        return 0.0

    # 属于某一分类的内容数量
    def cat_count(self, cat):
        if cat in self.cc:
            return float(self.cc[cat])
        return 0

    # 所有内容的数量
    def total_count(self):
        return sum(self.cc.values())

    # 所有内容的分类
    def categories(self):
        return self.cc.keys()

    def train(self, item, cat):
        features = self.get_features(item)
        for f in features:
            self.inc_f(f, cat)
        self.incc(cat)

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


if __name__ == "__main__":
    test_sentence = "Hi there, May  be you do not know me. But this is True"
    good_one = "Hi Pan, We are welcomed you are admitted!"
    # get_words(test_sentence)
    c1 = NaiveBayes(get_words)
    # c1.train(test_sentence, "bad")
    # c1.train(good_one, "good")
    # print(c1.f_count("pan", "good"))
    # print(c1.f_count("you", "bad"))
    sample_train(c1)
    # print(c1.f_prob("quick", "good"))
    # print(c1.cc)
    # sample_train(c1)
    # print(c1.weighted_prob("money", "good", c1.f_prob))
    print(c1.prob("quick rabbit", "good"))
