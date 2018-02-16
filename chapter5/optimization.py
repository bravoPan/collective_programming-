import time
import random
import math
from pprint import pprint

people = [
    ("Seymour", "BOS"),
    ("Franny", "DAL"),
    ("Zooey", "CAK"),
    ("Walt", "MIA"),
    ("Buddy", "ORD"),
    ("Les", "OMA")
]

destination = "LGA"

flights = {}

for line in open("schedule.txt"):
    origin, dest, depart, arrive, price = line.strip().split(",")
    flights.setdefault((origin, dest), [])
    flights[(origin, dest)].append((depart, arrive, int(price)))


def get_minutes(t):
    x = time.strptime(t, "%H:%M")
    return x[3] * 60 + x[4]


def print_schedule(r):
    total_price = 0
    for d in range(int(len(r) / 2)):
        # print(d)
        name = people[d][0]
        origin = people[d][1]
        out = flights[(origin, destination)][r[2 * d]]
        ret = flights[(destination, origin)][r[2 * d + 1]]
        total_price += out[2] + ret[2]
        print("%10s%10s %5s-%5s $%3s %5s-%5s $%3s " % (name, origin, out[0], out[1], out[2], ret[0], ret[1], ret[2]))
    print("%10s%10s" % ("total", total_price))


def schedule_cost(sol):
    total_price = 0
    latest_arrival = 0
    earliest_dep = 24 * 60

    for d in range(int(len(sol) / 2)):
        origin = people[d][1]
        outbound = flights[(origin, destination)][int(sol[2 * d])]
        returnf = flights[(destination, origin)][int(sol[2 * d + 1])]

        total_price += outbound[2]
        total_price += returnf[2]

        if latest_arrival < get_minutes(outbound[1]):
            latest_arrival = get_minutes(outbound[1])
        if earliest_dep > get_minutes(returnf[0]):
            earliest_dep = get_minutes(returnf[0])

    # get the wait time everyone
    total_wait = 0
    for d in range(int(len(sol) / 2)):
        origin = people[d][1]
        outbound = flights[(origin, destination)][int(sol[2 * d])]
        returnf = flights[(destination, origin)][int(sol[2 * d + 1])]
        total_wait += latest_arrival - get_minutes(outbound[1])
        total_wait += get_minutes(returnf[0]) - earliest_dep

    if latest_arrival > earliest_dep:
        total_price += 50

    return total_price + total_wait


# 随机搜索
def random_optimize(domain, costf):
    best = 99999999
    best_r = None
    for i in range(1000):
        r = [random.randint(domain[i][0], domain[i][1])
             for i in range(len(domain))]
        cost = costf(r)

        if cost < best:
            best = cost
            best_r = r
    return best_r


# 爬山法
def hill_climb(domain, costf):
    sol = [random.randint(domain[i][0], domain[i][1])
           for i in range(len(domain))]
    while 1:
        neighbors = []
        for j in range(len(domain)):
            if sol[j] > domain[j][0]:
                neighbors.append(sol[0:j] + [sol[j] - 1] + sol[j + 1:])
            if sol[j] < domain[j][1]:
                neighbors.append(sol[0:j] + [sol[j] + 1] + sol[j + 1:])

        current = costf(sol)
        best = current
        for j in range(len(neighbors)):
            cost = costf(neighbors[j])
            if cost < best:
                best = cost
                sol = neighbors[j]

        if best == current:
            break

    return sol


# 退火算法
def annealing_optimize(domain, costf, T=100000.0, cool=0.95, step=1):
    vec = [float(random.randint(domain[i][0], domain[i][1]))
           for i in range(len(domain))]
    while T > 0.1:
        #  创建一个索引
        i = random.randint(0, len(domain) - 1)
        # 选择一个改变索引值的方向
        dir = random.randint(-step, step)
        vecb = vec[:]
        vecb[i] += dir
        if vecb[i] < domain[i][0]:
            vecb[i] = domain[i][0]
        elif vecb[i] > domain[i][1]:
            vecb[i] = domain[i][1]

        ea = costf(vec)
        eb = costf(vecb)

        if eb < ea or random.random() < pow(math.e, -(eb - ea) / T):
            vec = vecb
            T = T * cool
    vec = [int(i) for i in vec]
    return vec


def genetic_optimize(domain, costf, popsize=50, step=1, muprob=0.2, elite=0.2, maxiter=100):
    # 控制变异
    def mutate(vec):
        i = random.randint(0, len(domain) - 1)
        if random.random() < 0.5 and vec[i] > domain[i][0]:
            return vec[0:i] + [vec[i] - step] + vec[i + 1:]
        elif vec[i] < domain[i][1]:
            return vec[0:i] + [vec[i] + step] + vec[i + 1:]
        else:
            return vec

    def cross_over(r1, r2):
        i = random.randint(1, len(domain) - 2)
        return r1[0:i] + r2[i:]

    pop = []
    for i in range(popsize):
        vec = [random.randint(domain[i][0], domain[i][1])
               for i in range(len(domain))]
        pop.append(vec)

    top_elite = int(elite * popsize)

    # print("The size of pop is " + str(len(pop)))

    for i in range(maxiter):
        scores = [(costf(v), v) for v in pop]
        # 由小到大
        scores.sort()
        ranked = [v for (s, v) in scores]

        pop = ranked[0:top_elite]

        while len(pop) < popsize:
            # 变异
            if random.random() < muprob:
                c = random.randint(0, top_elite)
                mutated_result = mutate(ranked[c])
                pop.append(mutated_result)
            # 交叉
            else:
                c1 = random.randint(0, top_elite)
                c2 = random.randint(0, top_elite)
                cross_result = cross_over(ranked[c1], ranked[c2])
                pop.append(cross_result)
        print(scores[0][0])

    return scores[0][1]


if __name__ == "__main__":
    # s = [1, 4, 3, 2, 7, 3, 6, 3, 2, 4, 5, 3]
    # pprint(schedule_cost(s))
    domain = [(0, 9)] * (len(people) * 2)
    # s = random_optimize(domain, schedule_cost)
    # print(schedule_cost(s))
    # s = hill_climb(domain, schedule_cost)
    # print_schedule(s)
    # print(schedule_cost(s))
    # s = annealing_optimize(domain, schedule_cost)
    # print_schedule(s)
    try:
        s = genetic_optimize(domain, schedule_cost)
        print_schedule(s)
    except:
        pass
