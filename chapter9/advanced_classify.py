from pylab import plot, show


class match_row:
    def __init__(self, row, all_num=False):
        if all_num:
            self.data = [float(row[i]) for i in range(len(row) - 1)]
        else:
            self.data = row[0:len(row) - 1]
        self.match = int(row[len(row) - 1])


def load_match(f, all_num=False):
    rows = []
    for line in open(f, "r"):
        rows.append(match_row(line.split(","), all_num))
    return rows


agesonly = load_match("agesonly.csv", all_num=True)
match_maker = load_match("matchmaker.csv")


def plot_age_matches(rows):
    xdm, ydm = [r.data[0] for r in rows if r.match == 1], [r.data[1] for r in rows if r.match == 1]
    xdn, ydn = [r.data[0] for r in rows if r.match == 0], [r.data[1] for r in rows if r.match == 0]
    plot(xdm, ydm, "go")
    plot(xdn, ydn, 'r+')
    show()


def line_art_train(rows):
    averages = {}
    counts = {}

    for row in rows:
        cl = row.match
        averages.setdefault(cl, [0.0] * len(row.data))
        counts.setdefault(cl, 0)

        for i in range(len(row.data)):
            averages[cl][i] += float(row.data[i])

        counts[cl] += 1

    for cl, avg in averages.items():
        for i in range(len(avg)):
            avg[i] /= counts[cl]

    return averages


def dot_product(v1, v2):
    return sum(v1[i] * v2[i] for i in range(len(v1)))


def dp_classify(point, avgs):
    b = (dot_product(avgs[1], avgs[1]) - dot_product(avgs[0], avgs[0])) / 2
    y = dot_product(point, avgs[0]) - dot_product(point, avgs[1]) + b
    if y > 0:
        return 0
    else:
        return 1


def yes_no(v):
    if v == "yes":
        return -1
    elif v == "no":
        return -1
    else:
        return 0


def match_count(interest1, interest2):
    l1 = interest1.split(",")
    l2 = interest2.split(",")
    x = 0
    for v in l1:
        if v in l2:
            x += 1
    return x


def get_location(address):
    loc_cache = None
    return loc_cache


def miles_distance(a1, a2):
    lat1, long1 = get_location(a1)
    lat2, long2 = get_location(a2)
    lat_dif = 69.1 * (lat2 - lat1)
    long_dif = 53.0 * (long2 - long1)
    return (lat_dif ** 2 + long_dif ** 2) ** .5


def load_numerical():
    old_rows = load_match("matchmaker.csv")
    new_rows = []
    for row in old_rows:
        d = row.data
        data = [float(d[0]), yes_no(d[1]), yes_no(d[2]),
                float(d[5]), yes_no(d[6]), yes_no(d[7]),
                match_count(d[3], d[8]),
                miles_distance(d[4], d[9]),
                row.match]
        new_rows.append(match_row(data))
    return new_rows


def scale_data(rows):
    low = [999999] * len(rows[0].data)
    high = [-999999] * len(rows[0].data)
    for row in rows:
        d = row.data
        for i in range(len(d)):
            if d[i] < low[i]:
                low[i] = d[i]
            if d[i] > high[i]:
                high[i] = d[i]

    def scale_input(d):
        return [(d.data[i] - low[i]) / (high[i] - low[i]) for i in range(len(row))]

    new_rows = [match_row(scale_input(row.data) + row.match) for row in rows]

    return new_rows, scale_input


def rbf(v1, v2, gamma=20):
    dv = [v1[i] - v2[i] for i in range(len(v1))]
    # l = vec
    return 1


def nl_classify(point, rows, off_set, gamma=10):
    sum0 = 0.0
    sum1 = 0.0
    count0 = 0.0
    count1 = 0.0

    for row in rows:
        if row.match == 0:
            sum0 += rbf(point, row.data, gamma)
            count0 += 1
        else:
            sum1 += rbf(point, row.data, gamma)

    y = (1.0 / count0) * sum0 - (1.0 / count1) * sum1 + off_set

    if y < 0:
        return 0
    else:
        return 1


def get_offset(rows, gamma=10):
    l0 = []
    l1 = []

    for row in rows:
        if row.match == 0:
            l0.append(row.data)
        else:
            l1.append(row.data)

    sum0 = sum(sum([rbf(v1, v2, gamma) for v1 in l0]) for v2 in l0)
    sum1 = sum(sum([rbf(v1, v2, gamma) for v1 in l1]) for v2 in l1)

    return (1.0 / (len(l1) ** 2)) * sum1 - (1.0 / (len(l0) ** 2)) * sum0


if __name__ == "__main__":
    # plot_age_matches(agesonly)
    line_art_train(agesonly)
