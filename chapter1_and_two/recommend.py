import math

users = ["樱花之眼", "浮华", "吧唧吧唧", "mypd", "Pan", "小岛木", "小草"]
movies = ["养家之人", "小萝莉的猴神大叔", "天上再见", "无手的少女", "比得兔", "无巧不成婚", "那就是我的世界", "金钱世界",
          "乐高DC超级英雄：闪电侠", "怪奇秀"]

critics = {
    'Pan': {'乐高DC超级英雄：闪电侠': 2.9,
            '小萝莉的猴神大叔': 2.7,
            '怪奇秀': 1.7,
            '无手的少女': 2.3,
            '比得兔': 3.5,
            '金钱世界': 0.5},
    'mypd': {'乐高DC超级英雄：闪电侠': 2.5,
             '天上再见': 0.6,
             '小萝莉的猴神大叔': 4.9,
             '无巧不成婚': 0.3,
             '无手的少女': 1.9,
             '金钱世界': 4.3},
    '吧唧吧唧': {'天上再见': 3.7,
             '小萝莉的猴神大叔': 4.7,
             '无巧不成婚': 1.6,
             '无手的少女': 2.0,
             '比得兔': 1.9,
             '那就是我的世界': 3.1},
    '小岛木': {'乐高DC超级英雄：闪电侠': 3.6,
            '小萝莉的猴神大叔': 2.1,
            '怪奇秀': 2.8,
            '无巧不成婚': 4.2,
            '那就是我的世界': 1.9,
            '金钱世界': 1.5},
    '小草': {'天上再见': 1.9,
           '小萝莉的猴神大叔': 1.6,
           '无巧不成婚': 0.7,
           '比得兔': 3.3,
           '那就是我的世界': 1.4,
           '金钱世界': 3.1},
    '樱花之眼': {'养家之人': 3.6,
             '小萝莉的猴神大叔': 2.3,
             '无巧不成婚': 1.1,
             '无手的少女': 0.4,
             '比得兔': 1.2,
             '那就是我的世界': 3.1},
    '浮华': {'养家之人': 1.1,
           '天上再见': 3.6,
           '怪奇秀': 3.0,
           '无巧不成婚': 4.9,
           '比得兔': 4.4,
           '金钱世界': 1.1}
}


def sim_distance(prefs, person1, person2):
    # 创建一个字典，此处person1是需要交友的，所以我们需要
    # 判断person1中哪些电影是person2看过的
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1
            # 很不巧person2看过的电影person1一部都没看过，还交啥友，返回0呗
    if len(si) == 0:
        return 0

    # 1 / (1 + math.sqrt(sum_of_squares))，为什么给分母加1呢？因为math.sqrt()可能会返回0，所以程序就会出错
    sum_of_squares = sum(math.pow(prefs[person1][item] - prefs[person2][item], 2) for item in si)
    return 1 / (1 + math.sqrt(sum_of_squares))


def sim_person(prefs, person1, person2):
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1

    n = len(si)

    if len(si) == 0:
        return 0

    # 对应上面公式x的求和
    sum1 = sum([prefs[person1][it] for it in si])
    sum2 = sum([prefs[person2][it] for it in si])

    # 对应上面公式y的求和
    pow_sum1 = sum([math.pow(prefs[person1][it], 2) for it in si])
    pow_sum2 = sum([math.pow(prefs[person2][it], 2) for it in si])

    # 对应上面公式xy的求和
    pSum = sum([prefs[person1][it] * prefs[person2][it] for it in si])

    num = pSum - (sum1 * sum2 / n)
    den = math.sqrt((pow_sum1 - pow(sum1, 2) / n) * (pow_sum2 - pow(sum2, 2) / n))

    if den == 0:
        return 0

    r = num / den
    return r


def topMatches(prefs, person, n=5, similarity=sim_person):
    scores = [(similarity(prefs, person, other), other) for other in prefs if person != other]

    scores.sort()
    scores.reverse()
    return scores[0:n]


def get_recommendation(prefs, person, similarity=sim_person):
    totals = {}
    sim_sum = {}

    for other in prefs:
        if other == person:
            continue

        # 平价值小于0的不要
        sim = similarity(prefs, person, other)
        if sim < 0:
            continue

        for item in prefs[other]:
            # 只对自己没看过的电影做评价
            if item not in prefs[person] or prefs[person][item] == 0:
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim

                # 相似度之和
                sim_sum.setdefault(item, 0)
                sim_sum[item] += sim

    ranking = [(total / sim_sum[item], item) for item, total in totals.items() if sim_sum[item] != 0]
    ranking.sort()
    ranking.reverse()
    return ranking


def recommend_all(prefers):
    for i in users:
        print(i + ":", end="")
        print("%5s" % "", end="")
        print(get_recommendation(prefers, i))


if __name__ == "__main__":
    # pprint(get_recommendation(critics, "Pan"))
    recommend_all(prefers=critics)