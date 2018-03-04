from random import random, randint
import math
from chapter5 import optimization
from matplotlib import *
from numpy import arange, array
from pylab import plot, show

weight_domain = [(0, 20)] * 4


def wine_price(rating, age):
    peak_age = rating - 50

    price = rating / 2
    if age > peak_age:
        # 5年后品质会变差
        price = price * (5 - (age - peak_age))
    else:
        # 价格在接近峰值年的时候增加5倍
        price *= (5 * ((age + 1) / peak_age))
    if price < 0:
        price = 0
    return price


def wine_set1():
    rows = []
    for i in range(300):
        rating = random() * 50 + 50
        age = random() * 50
        price = wine_price(rating, age)

        price *= (random() * 0.4 + 0.8)
        rows.append({"input": (rating, age), "result": price})
    return rows


def euclidean(v1, v2):
    d = 0.0
    for i in range(len(v1)):
        d += (v1[i] - v2[i]) ** 2
    return math.sqrt(d)


def get_distance(data, vec1):
    distance_list = []
    for i in range(len(data)):
        vec2 = data[i]["input"]
        distance_list.append((euclidean(vec1, vec2), i))
    distance_list.sort()
    return distance_list


def knn_estimate(data, vec1, k=5):
    dist = get_distance(data, vec1)
    avg = 0.0
    for i in range(k):
        idx = dist[i][1]
        avg += data[idx]["result"]
    avg /= k
    return avg

def inverse_weight(dist, num=1.0, const=0.1):
    return num / (dist + const)

def subtract_weight(dist, const=1.0):
    if dist > const:
        return 0
    else:
        return const - dist


def gaussian(dist, sigma=10.0):
    return math.e ** (-dist ** 2 / (2 * sigma ** 2))


def weighted_knn(data, vec1, k=5, weight_f=gaussian):
    dlist = get_distance(data, vec1)
    avg = 0.0
    total_weight = 0.0

    for i in range(k):
        dist = dlist[i][0]
        idx = dlist[i][1]
        weight = weight_f(dist)
        avg += weight * data[idx]["result"]
        total_weight += weight
    avg /= total_weight
    return avg


def divide_data(data, test=0.05):
    train_set = []
    test_set = []
    for row in data:
        if random() < test:
            test_set.append(row)
        else:
            train_set.append(row)
    return train_set, test_set


def test_algorithm(alg_f, train_set, test_set):
    error = 0.0
    for row in test_set:
        guess = alg_f(train_set, row["input"])
        error += (row["result"] - guess) ** 2
    return error / len(test_set)


def cross_validate(algf, data, trials=100, test=0.05):
    error = 0.0
    for i in range(trials):
        train_set, test_set = divide_data(data, test)
        error += test_algorithm(algf, train_set, test_set)
    return error / trials


def wine_set2():
    rows = []
    for i in range(300):
        rating = random() * 50 + 50
        age = random() * 50
        aisle = float(randint(1, 20))
        bottle_size = [375.0, 750, 1500, 3000][randint(0, 3)]
        price = wine_price(rating, age)
        price *= (bottle_size / 750)
        price *= random() * 0.9 + 0.2
        rows.append({"input": (rating, age, aisle, bottle_size),
                     "result": price})
    return rows


def rescale(data, scale):
    scale_data = []
    for row in data:
        scaled = [scale[i] * row["input"][i] for i in range(len(scale))]
        scale_data.append({"input": scaled, "result": row["result"]})
    return scale_data


def knn3(d, v):
    return knn_estimate(d, v, k=3)


def create_cost_function(alg_f, data):
    def cost_f(scale):
        s_data = rescale(data, scale)
        return cross_validate(alg_f, s_data, trials=10)

    return cost_f


def wine_set3():
    rows = wine_set1()
    for row in rows:
        if random() < 0.5:
            row["result"] *= 0.5
    return rows


def prob_guess(data, vec1, low, high, k=5, weight_f=gaussian):
    d_list = get_distance(data, vec1)
    n_weight = 0.0
    t_weight = 0.0

    for i in range(k):
        dist = d_list[i][0]
        idx = d_list[i][1]
        weight = weight_f(dist)
        v = data[idx]["result"]
        if low <= v <= high:
            n_weight += weight
        t_weight += weight

    if t_weight == 0:
        return 0
    return n_weight / t_weight


def cumulative_graph(data, vec1, high, k=5, weight_f=gaussian):
    t1 = arange(0.0, high, 0.1)
    # print([v for v in t1])
    c_prob = array([prob_guess(data, vec1, 0, v, k, weight_f) for v in t1])
    plot(t1, c_prob)
    show()



if __name__ == "__main__":
    data = wine_set2()
    # print(data)
    s_data = rescale(data, [10, 10, 0, 0.5])
    # print(cross_validate(weighted_knn, s_data))
    # cost_f = create_cost_function(knn_estimate, data)
    # data = wine_set3()
    cumulative_graph(data, (1, 1), 120)
