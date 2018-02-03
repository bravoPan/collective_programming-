import math

from chapter1_and_two.recommendation import critics


# 欧几里得距离法
# return the similarity of two people
def sim_distance(prefs, person1, person2):
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1

    if len(si) == 0:
        return 0

    # return the sum of the similar items
    sum_of_squares = sum(math.pow(prefs[person1][item] - prefs[person2][item], 2) for item in si)
    return 1 / (1 + math.sqrt(sum_of_squares))


# Pearson Correlation Score
def sim_person(prefs, person1, person2):
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1

    n = len(si)

    if len(si) == 0:
        return 0

    # compute sum of similar items
    sum1 = sum([prefs[person1][it] for it in si])
    sum2 = sum([prefs[person2][it] for it in si])

    # compute power sum of similar items
    pow_sum1 = sum([math.pow(prefs[person1][it], 2) for it in si])
    pow_sum2 = sum([math.pow(prefs[person2][it], 2) for it in si])

    # compute product sum
    pSum = sum([prefs[person1][it] * prefs[person2][it] for it in si])

    num = pSum - (sum1 * sum2 / n)
    den = math.sqrt((pow_sum1 - pow(sum1, 2) / n) * (pow_sum2 - pow(sum2, 2) / n))

    if den == 0:
        return 0

    r = num / den
    return r


if __name__ == "__main__":
    print("The Euclid method is : " + str(sim_distance(critics, 'Lisa Rose', 'Gene Seymour')))
    print("The person method is: " + str(sim_person(critics, 'Lisa Rose', 'Gene Seymour')))
