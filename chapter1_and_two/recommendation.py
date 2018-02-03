#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 18:42:56 2018

@author: yuanxiansen
"""

import csv
from pprint import pprint

critics = {
    'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5, 'Superman Returns': 3.5,
                  'You, Me and Dupree': 2.5, 'The Night Listener': 3.0, 'Just My Luck': 3.0},
    'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5, 'Just My Luck': 1.5, 'The Night Listener': 3.0,
                     'You, Me and Dupree': 3.5, 'Superman Returns': 5.0},
    'Michael Phillips': {'Lady in the Water': 2.5, 'Superman Returns': 3.5,
                         'The Night Listener': 4.0, 'Snitch': 2.0, 'Snakes on a Plane': 3.0},
    'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0, 'The Night Listener': 4.5, 'Superman Returns': 4.0,
                     'You, Me and Dupree': 2.5},
    'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0, 'Just My Luck': 2.0, 'Superman Returns': 3.0,
                     'You, Me and Dupree': 2.0, 'The Night Listener': 3.0},
    'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                      'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
    'Toby': {'Snakes on a Plane': 4.5, 'Superman Returns': 4.0, 'You, Me and Dupree': 1.0},
}

transform_critics = {
    'Lady in the Water': {'Lisa Rose': 2.5, 'Gene Seymour': 3.0},
    'Snakes on a Plane': {'Lisa Rose': 3.5, 'Gene Seymour': 3.5}
}


def load_movie_lens(path="./ml-latest-small"):
    movies = {}
    counter = 0
    reader = csv.reader(open(path + "/movies.csv", encoding="utf-8"))
    for movie_id, title, genera in reader:
        if counter == 0:
            counter += 1
            continue
        else:
            movies[movie_id] = title

    # 获取电影评分
    prefes = {}
    for userId, movieId, rating, timestamp in csv.reader(open(path + "/ratings.csv", encoding="utf-8")):
        if counter == 1:
            counter += 1
            continue
        else:
            prefes.setdefault(userId, {})
            prefes[userId][movies[movieId]] = float(rating)
    return prefes


if __name__ == "__main__":
    test = load_movie_lens()
    pprint(test)
