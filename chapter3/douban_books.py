from bs4 import BeautifulSoup
import requests
from pprint import pprint
import time
import json

url = "https://www.douban.com/people/cat221/"
reader_dict = {}
count = 0

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) '
                  'AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/46.0.2490.76 Mobile Safari/537.36',
    'Cookie': 'gr_user_id=f2cdf948-5be9-4c63-8454-d46a2169968e; _ga=GA1.2.1728400560.1468245480; __yadk_uid=fzZzb6DHq7TkCCP7zigVKCgL539HbS8Q; bid=EZfpqIMapdY; ll="118371"; _vwo_uuid_v2=6467E6163706A52D9EE52D1A2D477309|577b66cfce5b04547677823e76cecdba; __utmv=30149280.15386; ap=1; viewed="27667251_27131538_1851051_19952400_1607478_1754836_4820710_1008145_5299764_3280882"; __utmc=30149280; as="https://movie.douban.com/subject/26862688/?tag=%E7%83%AD%E9%97%A8&from=gaia"; ps=y; push_noty_num=0; push_doumail_num=0; dbcl2="153863611:4bRcb3d01vA"; ck=VSpb; __utmz=30149280.1517736432.142.115.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/login; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1517746837%2C%22https%3A%2F%2Faccounts.douban.com%2Flogin%3Falias%3D793175713%2540qq.com%26redir%3Dhttps%253A%252F%252Fwww.douban.com%252Fpeople%252Fcat221%252F%26source%3DNone%26error%3D1013%22%5D; _pk_ses.100001.8cb4=*; __utma=30149280.1728400560.1468245480.1517736432.1517746839.143; __utmt=1; _pk_id.100001.8cb4=c85f65bf6943eabc.1468246243.93.1517746930.1517736443.; __utmb=30149280.4.10.1517746839'
}

proxies = {"ip": "https://113.110.208.129"}
requested_list = []


def get_100_user(url, count):
    pprint(reader_dict)
    print(" " * count + "-", end="")
    # pprint(len(reader_dict))
    # 递归条件
    if len(reader_dict) >= 100:
        pprint(reader_dict)
        return
    # 判断留言板是否有用户
    wb_data = requests.get(url, proxies=proxies)
    soup = BeautifulSoup(wb_data.text, "lxml")
    user_name = soup.select("head > title")[0].text.strip()
    print(user_name)
    if user_name in reader_dict:
        return
    reader_dict.setdefault(user_name, [])
    book_soup = soup.find(id="book")
    user_soup = soup.find_all(id="board")
    if book_soup:
        books_a_tags = [i.find("a") for i in book_soup.find_all(class_="aob")]
        books_tag = [i.get("title") for i in books_a_tags]
        [reader_dict[user_name].append(i) for i in books_tag]
        if user_soup:
            friends_url = set([i.get("href") for i in user_soup[0].find("ul").find_all("a")])
            requested_url = friends_url - set(requested_list)
            [requested_list.append(i) for i in friends_url if i not in requested_list]
            for i in requested_url:
                time.sleep(3)
                get_100_user(i, count + 1)


if __name__ == "__main__":
    get_100_user(url, 0)
    pprint(reader_dict)

    with open("reader_prefes.txt", "w", encoding="utf-8") as f:
        json.dump(reader_dict, f)
