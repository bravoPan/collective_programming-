from bs4 import BeautifulSoup
import requests
from zhon import hanzi
import jieba
from collections import Counter
from chapter3.jianshu.config import __chinese_meaningless_word__


class ZhiDailyNewsAPI(object):
    def __init__(self):
        self.headers = headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) '
                          'AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/46.0.2490.76 Mobile Safari/537.36'
        }
        self.url = "https://zhuanlan.zhihu.com/api/columns/happymuyi/posts?limit=100"
        wb_data = requests.get(self.url, headers=headers)
        soup = BeautifulSoup(wb_data.text, "lxml").text
        parser_info_list = eval(soup.replace("false", "False").replace("null", "None").replace("true", "True"))
        # pprint(parser_info_list)
        all_article_info = []
        for i in parser_info_list:
            article_info = {}
            article_info.setdefault("title", i["title"])
            article_info.setdefault("content", i["content"])
            all_article_info.append(article_info)
        # list format
        self.data = all_article_info

    def get_article_size(self):
        return len(self.data)

    def get_article(self, size=10):
        if size > self.get_article_size():
            return False
        return self.data[0:size]

    def save_as_text(self, name="article", write_item=["title", "content"], size=10):
        if size > self.get_article_size():
            return False
        with open(name + ".txt", "w", encoding="utf-8") as f:
            for i in self.data[0:size]:
                for j in write_item:
                    f.write(i[j])
                    f.write("\n")
                f.write("\n")


class ArticleAnalyze(ZhiDailyNewsAPI):
    def get_article_analyze(self, n=5):
        # test the first article
        article_size = self.get_article_size()
        all_article = self.get_article(article_size)
        analyze_list = []
        for i in all_article:
            article_word_count = {}
            article_word_count["title"] = i["title"]
            article_word_count["content"] = self.get_single_article_analyze(i["content"])
            analyze_list.append(article_word_count)
        return analyze_list[0:n]

    def save_article_analyze(self, n=5):
        with open("word_count.txt", "w", encoding="utf-8") as f:
            for i in self.get_article_analyze(n=n):
                f.write(i["title"])
                f.write("\n")
                f.write(str((i["content"])))
                f.write("\n")
                f.write("\n")

    @staticmethod
    def get_single_article_analyze(content):
        seg_list = jieba.cut_for_search(content)
        word_dict = Counter(seg_list)
        print(word_dict)
        word_list = list(word_dict)
        # remove SBC case
        filter_list = hanzi.punctuation + "".join(__chinese_meaningless_word__)
        # filter the ready-filtered works
        for i in filter_list:
            if i in word_list:
                del word_dict[i]
        sorted_dict = sorted(word_dict.items(), key=lambda t: t[1], reverse=True)
        print(sorted_dict)
        return sorted_dict


if __name__ == "__main__":
    test = ZhiDailyNewsAPI()
    # pprint(test.get_article(size=100))
    test = ArticleAnalyze()
    # test.get_article_analyze()
    test.save_article_analyze(n=test.get_article_size())
