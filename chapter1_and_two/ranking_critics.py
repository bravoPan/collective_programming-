from pprint import pprint

from judge import sim_person, sim_distance

from chapter1_and_two import recommendation


def topMatches(prefs, person, n=5, similarity=sim_person):
    scores = [(similarity(prefs, person, other), other) for other in prefs if person != other]

    scores.sort()
    scores.reverse()
    return scores[0:n]


# print(topMatches(recommendation.critics, 'Toby', n=3))

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


def transform_prefers(prefes):
    result = {}
    for person in prefes:
        for item in prefes[person]:
            result.setdefault(item, {})
            result[item][person] = prefes[person][item]

    return result


def calculate_similarity_items(prefers, n=10):
    result = {}
    item_prefers = transform_prefers(prefers)
    c = 0
    for item in item_prefers:
        c += 1
        if c % 100 == 0:
            print("{} / {}".format(c, len(item_prefers)))
        # 寻找最相近的物品
        scores = topMatches(item_prefers, item, n=n, similarity=sim_distance)
        result[item] = scores
    return result


item_sim = calculate_similarity_items(recommendation.critics)


def get_recommended_item(prefers, item_match, user):
    user_rating = prefers[user]
    scores = {}
    total_sim = {}

    for (item, rating) in user_rating.items():
        for (similiarity, item2) in item_match[item]:

            # 如果用户对当前物品做过评价就跳过
            if item2 in user_rating:
                continue

            scores.setdefault(item2, 0)
            scores[item2] += similiarity * rating

            total_sim.setdefault(item2, 0)
            total_sim[item2] += similiarity
    # print([(score, item) for score, item in scores.items()])
    # print(total_sim)
    ranking = [(score / total_sim[item], item) for item, score in scores.items() if total_sim[item] != 0]
    ranking.sort()
    ranking.reverse()
    return ranking


if __name__ == "__main__":
    # transform_critics = transform_prefers(recommendation.critics)
    # print(transform_critics)
    # print(get_recommendation(transform_critics, 'Snakes on a Plane'))
    # pprint(calculate_similarity_items(recommendation.critics))
    # print(get_recommended_item(recommendation.critics, item_sim, 'Toby'))
    # pprint(get_recommendation(recommendation.load_movie_lens(), '87')[0:30])
    pprint(calculate_similarity_items(recommendation.load_movie_lens(), n=50))
