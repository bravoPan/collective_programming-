import random
import math
from chapter5.optimization import random_optimize, genetic_optimize

dorms = ["Zeus", "Athena", "Hercules", "Bacchus", "Pluto"]
prefers = [
    ("Toby", ("Bacchus", "Hercules")),
    ("Steve", ("Zeus", "Pluto")),
    ("Andrea", ("Athena", "Zeus")),
    ("Sarah", ("Zeus", "Pluto")),
    ("Dave", ("Athena", "Bacchus")),
    ("Jeff", ("Hercules", "Pluto")),
    ("Fred", ("Pluto", "Athena")),
    ("Suzie", ("Bacchus", "Hercules")),
    ("Laura", ("Bacchus", "Hercules")),
    ("Neil", ("Hercules", "Athena"))
]

domain = [(0, (len(dorms) * 2) - i - 1) for i in range(0, len(dorms) * 2)]


def print_solution(vec):
    slots = []
    for i in range(len(dorms)):
        slots += [i, i]

    for i in range(len(vec)):
        x = int(vec[i])

        dorm = dorms[slots[x]]
        print(prefers[i][0], dorm)
        del slots[x]


# print_solution([0, 1, 0, 0, 0, 0, 0, 0, 0, 0])

def dorm_cost(vec):
    cost = 0
    slots = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]
    for i in range(len(vec)):
        x = int(vec[i])
        dorm = dorms[slots[x]]
        pref = prefers[i][1]
        if pref[0] == dorm:
            cost += 0
        elif pref[1] == dorm:
            cost += 1
        else:
            cost += 3
        del slots[x]
    return cost


if __name__ == "__main__":
    # s = random_optimize(domain, dorm_cost)
    # print(s)
    s = genetic_optimize(domain, dorm_cost)
    # print(dorm_cost(s))
