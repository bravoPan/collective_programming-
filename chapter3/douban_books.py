from bs4 import BeautifulSoup
import requests
from pprint import pprint
import time
from chapter3.config import readers
import json
import re

url = "https://www.douban.com/people/cat221/"
user_url = "https://www.douban.com/note/187876507/"
reader_dict = {}
count = 0

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) '
                  'AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/46.0.2490.76 Mobile Safari/537.36',
    'Cookie': 'gr_user_id=f2cdf948-5be9-4c63-8454-d46a2169968e; _ga=GA1.2.1728400560.1468245480; __yadk_uid=fzZzb6DHq7TkCCP7zigVKCgL539HbS8Q; bid=EZfpqIMapdY; ll="118371"; _vwo_uuid_v2=6467E6163706A52D9EE52D1A2D477309|577b66cfce5b04547677823e76cecdba; __utmv=30149280.15386; ap=1; viewed="27667251_27131538_1851051_19952400_1607478_1754836_4820710_1008145_5299764_3280882"; __utmc=30149280; as="https://movie.douban.com/subject/26862688/?tag=%E7%83%AD%E9%97%A8&from=gaia"; ps=y; push_noty_num=0; push_doumail_num=0; dbcl2="153863611:4bRcb3d01vA"; ck=VSpb; __utmz=30149280.1517736432.142.115.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/login; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1517746837%2C%22https%3A%2F%2Faccounts.douban.com%2Flogin%3Falias%3D793175713%2540qq.com%26redir%3Dhttps%253A%252F%252Fwww.douban.com%252Fpeople%252Fcat221%252F%26source%3DNone%26error%3D1013%22%5D; _pk_ses.100001.8cb4=*; __utma=30149280.1728400560.1468245480.1517736432.1517746839.143; __utmt=1; _pk_id.100001.8cb4=c85f65bf6943eabc.1468246243.93.1517746930.1517736443.; __utmb=30149280.4.10.1517746839'
}

# A new api interface
reader_name_list = []

proxies = {"ip": "https://113.110.208.129"}
requested_list = []


# <-------------------------------------------old method, but unexpected------------------------------------>

def get_100_user(url, count):
    print(" " * count + "-", end="")
    # pprint(len(reader_dict))
    # 递归条件
    if len(reader_dict) >= 100:
        pprint(reader_name_list)
        return
    # 判断留言板是否有用户
    wb_data = requests.get(url, proxies=proxies)
    if wb_data.status_code == 200:
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
                    try:
                        reader_name_list.append(get_user_name(i))
                    except:
                        pass
                    get_100_user(i, count + 1)


def test_url(url):
    return requests.get(url).status_code


def collect_book():
    book_dict = {}
    for i in readers:
        for book in readers[i]:
            book_dict.setdefault(book, 0)
            book_dict[book] += 1

    book_dict = sorted(book_dict.items(), key=lambda x: x[1], reverse=True)
    pprint(book_dict)


# <-------------------------------------------old method, but unexpected------------------------------------>

def get_user_name(url):
    match_symbol = re.compile(r"https://www.douban.com/people/(\w+)?")
    name = match_symbol.match(url).group(1)
    return name


def get_dou_user(url):
    wb_data = requests.get(url)
    soup = BeautifulSoup(wb_data.text, "lxml")
    user_tags = soup.find_all(rel="nofollow")
    pure_name_list = [get_user_name(i.get("href")) for i in user_tags if
                      "https://www.douban.com/people" in i.get("href")]
    return pure_name_list


def get_books(name):
    contact_url = "https://api.douban.com/v2/book/user/{}/collections".format(name)
    wb_data = requests.get(contact_url, headers=headers, proxies=proxies)
    reader_collect_dict = eval(wb_data.text)
    pprint(reader_collect_dict)
    api_summary_list = [i["book"]["summary"] for i in reader_collect_dict["collections"]]
    current_books = []
    books_title = map(parser_book_from_summary, api_summary_list)
    [[current_books.append(j) for j in i] for i in books_title if i]
    if current_books:
        reader_dict.setdefault(name, [])
        # [pprint(i) for i in books_title]
        # all_book_sets = [parser_book_from_summary(summary) for summary in api_summary_list if
        #                  parser_book_from_summary(summary)]
        # pprint(all_book_sets)
        reader_dict[name] = list(set(current_books))


def parser_book_from_summary(summary):
    pattern = re.compile("《(\w+)》")
    book_titles = set(re.findall(pattern, summary))
    if book_titles:
        return book_titles
    else:
        return None


# <-------------------------------------------load json and analyze------------------------------------>
def load_json_readers():
    return eval(json.load(open("new_douban.json", encoding="utf-8")))[0]


def book_to_reader():
    new_reader_dict = load_json_readers()
    books = {}
    for reader in new_reader_dict:
        for book in new_reader_dict[reader]:
            books.setdefault(book, 0)
            books[book] += 1
    # result = sorted(books.items(), key=lambda t: t[1], reverse=False)
    # return result
    dict_keys = list(books.keys())
    for i in dict_keys:
        if books[i] <= 2:
            del books[i]
    return books


def create_matrix():
    book_names = book_to_reader()
    labels = book_names.keys()
    readers_prefer_lists = []
    reader_to_book = load_json_readers()
    index = 0
    readers = []
    for i in reader_to_book:
        readers.append(i)
        readers_prefer_lists.append([])
        for j in labels:
            if j in reader_to_book[i]:
                readers_prefer_lists[index].append(1)
            else:
                readers_prefer_lists[index].append(0)
        index += 1
    return readers, readers_prefer_lists, labels


def write_file():
    readers, data, labels = create_matrix()
    out = open("douban.txt", "w", encoding="utf-8")
    out.write("Books")
    for user in readers:
        out.write("\t{}".format(user))
    out.write("\n")
    index = 0
    for i in labels:
        out.write(i + "\t")
        for t in data[index]:
            out.write(str(t) + "\t")
        out.write("\n")
        index += 1
    pprint(len(readers))
    pprint("rows are " + str(len(data)) + "columns are " + str(len(data[0])))
    pprint(len(labels))


if __name__ == "__main__":
    # book_to_reader()
    # create_matrix()
    # write_file()
    # user_lists = get_dou_user(user_url)[0:200]
    # try:
    #     [get_books(i) for i in user_lists]
    # except:
    #     pass
    # test_json = json.dumps([reader_dict])
    # with open("new_douban.json", "w", encoding="utf-8") as f:
    #     json.dump(test_json, f)
    # dou_dict = eval(json.load(open("new_douban.json", encoding="utf-8")))[0]
    # pprint(dou_dict)
    # create_matrix()
    # write_file()
    get_books("cat221")
