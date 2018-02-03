from bs4 import BeautifulSoup
import requests
from pprint import pprint
import json

wb_data = requests.get("http://is.snssdk.com/api/news/feed/v51/?category=news_car")
dict_info = str(wb_data.content, encoding="utf-8").replace("\\", "")
pprint(dict_info)
# pprint(info_dict)
