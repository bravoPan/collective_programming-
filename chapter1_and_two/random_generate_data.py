import random
import math
from pprint import pprint

users = ["樱花之眼", "浮华", "吧唧吧唧", "mypd", "Pan", "小岛木", "小草"]
movies = ["养家之人", "小萝莉的猴神大叔", "天上再见", "无手的少女", "比得兔", "无巧不成婚", "那就是我的世界", "金钱世界",
          "乐高DC超级英雄：闪电侠", "怪奇秀"]

preferences = {}


def random_personal_prefers():
    random_movies = []
    selected_movies = movies[:]
    for i in range(6):
        random_movie = random.choice(selected_movies)
        random_movies.append(random_movie)
        selected_movies.remove(random_movie)
    random_dicts = {}
    for i in random_movies:
        random_dicts[i] = round(random.random() * 5, 1)
    return random_dicts


for i in users:
    preferences.setdefault(i, {})
    preferences[i] = random_personal_prefers()

# pprint(preferences)
