from bs4 import BeautifulSoup
import requests
from pprint import pprint


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


if __name__ == "__main__":
    test = ZhiDailyNewsAPI()
    pprint(test.get_article(size=100))
    # test.save_as_text(size=100)
