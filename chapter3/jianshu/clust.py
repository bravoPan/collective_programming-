from math import sqrt
from PIL import Image, ImageDraw, ImageFont
import random


def readfile(filename):
    lines = open(filename, encoding="utf-8").readlines()

    col_names = lines[0].strip().split("\t")[1:]
    row_names = []
    data = []
    for line in lines[1:]:
        p = line.strip().split('\t')
        row_names.append(p[0])
        data.append([float(x) for x in p[1:]])
    return row_names, col_names, data


def pearson(v1, v2):
    # 简单求和
    sum1 = sum(v1)
    sum2 = sum(v2)

    # 求平方和
    sum1_sq = sum([pow(x, 2) for x in v1])
    sum2_sq = sum([pow(x, 2) for x in v2])

    # 求平方和
    p_sum = sum([v1[i] * v2[i] for i in range(len(v1))])

    num = p_sum - (sum1 * sum2 / len(v1))
    den = sqrt((sum1_sq - pow(sum1, 2) / len(v1)) * (sum2_sq - pow(sum2, 2) / len(v2)))

    if den == 0:
        return 0
    return 1.0 - num / den


class BiCluster:
    def __init__(self, vec, left=None, right=None, distance=0.0, id=None):
        self.left = left
        self.right = right
        self.vec = vec
        self.id = id
        self.distance = distance


def h_cluster(rows, distance=pearson):
    distances = {}
    current_cluster_id = -1

    clust = [BiCluster(rows[i], id=i) for i in range(len(rows))]

    while len(clust) > 1:
        lowest_pair = (0, 1)
        closest = distance(clust[0].vec, clust[1].vec)

        for i in range(len(clust)):
            for j in range(i + 1, len(clust)):
                if (clust[i].id, clust[j].id) not in distances:
                    distances[(clust[i].id, clust[j].id)] = distance(clust[i].vec, clust[j].vec)

                d = distances[(clust[i].id, clust[j].id)]
                if d < closest:
                    closest = d
                    lowest_pair = (i, j)

        mergevec = [
            (clust[lowest_pair[0]].vec[i] + clust[lowest_pair[1]].vec[i]) / 2.0 for i in range(len(clust[0].vec))
        ]

        # 建立新的聚类
        new_cluster = BiCluster(mergevec, left=clust[lowest_pair[0]], right=clust[lowest_pair[1]], distance=closest,
                                id=current_cluster_id)

        current_cluster_id -= 1
        del clust[lowest_pair[1]]
        del clust[lowest_pair[0]]
        clust.append(new_cluster)

    return clust[0]


def print_clust(clust, labels=None, n=0):
    print(" " * n, end="")
    if clust.id < 0:
        print("-")
    else:
        if labels == None:
            print(clust.id)
        else:
            print(labels[clust.id])
    if clust.left != None:
        print_clust(clust.left, labels=labels, n=n + 1)
    if clust.right != None:
        print_clust(clust.right, labels=labels, n=n + 1)


def get_height(clust):
    if clust.left == None and clust.right == None:
        return 1
    return get_height(clust.left) + get_height(clust.right)


def get_depth(clust):
    if clust.left == None and clust.right == None:
        return 0
    return max(get_depth(clust.left), get_depth(clust.right)) + clust.distance


def draw_den_drog_gram(clust, labels, jpeg="clusters.jpg"):
    h = get_depth(clust) * 220
    w = 1200
    depth = get_depth(clust)
    scaling = float(w - 300) / depth
    img = Image.new("RGB", (w, int(h)), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw_node(draw, clust, 10, (h / 2), scaling, labels)
    img.save(jpeg, "JPEG")


def draw_node(draw, clust, x, y, scaling, labels):
    if clust.id < 0:
        h1 = get_height(clust.left) * 40
        h2 = get_height(clust.right) * 40
        top = y - (h1 + h2) / 2
        bottom = y + (h1 + h2) / 2
        ll = clust.distance * scaling

        draw.line((x, top + h1 / 2, x, bottom - h2 / 2), fill=(255, 0, 0))
        draw.line((x, top + h1 / 2, x + ll, top + h1 / 2), fill=(255, 0, 0))
        draw.line((x, bottom - h2 / 2, x + ll, bottom - h2 / 2), fill=(255, 0, 0))

        draw_node(draw, clust.left, x + ll, top + h1 / 2, scaling, labels)
        draw_node(draw, clust.right, x + ll, bottom - h2 / 2, scaling, labels)
    else:
        font = ImageFont.truetype("/Library/Fonts/Arial Unicode.ttf")
        draw.text((x + 10, y - 7), labels[clust.id], (0, 0, 0), font=font)


def k_cluster(rows, distance=pearson, k=4):
    # 寻找每个点的最大值和最小值random.random() * (ranges[i][1] - ranges[i][0]) + ranges[i][0]
    ranges = [(min([row[i] for row in rows]), max([row[i] for row in rows]))
              for i in range(len(rows[0]))]

    # 创建k个中心点，k为随机创建的聚类中心点个数，
    clusters = [[random.random() * (ranges[i][1] - ranges[i][0]) + ranges[i][0]
                 for i in range(len(rows[0]))]
                for j in range(k)]

    last_matches = None
    # 循环聚类次数
    for t in range(100):
        print("Iteration {}".format(t))
        best_matches = [[] for i in range(k)]

        # 和分级聚类的计算方法都相似就是求最相似的点
        for j in range(len(rows)):
            row = rows[j]
            best_match = 0
            for i in range(k):
                d = distance(clusters[i], row)
                if d < distance(clusters[best_match], row):
                    best_match = i
            #
            best_matches[best_match].append(j)

        if best_matches == last_matches:
            break
        last_matches = best_matches

        # 重新计算聚类中心点的平均值,把中心点移到平均位置处
        for i in range(k):
            avgs = [0.0] * len((rows[0]))
            if len(best_matches[i]) > 0:
                for row_id in best_matches[i]:
                    for m in range(len(rows[row_id])):
                        avgs[m] += rows[row_id][m]

                for j in range(len(avgs)):
                    avgs[j] /= len(best_matches[i])
                clusters[i] = avgs
    return best_matches


def scale_down(data, distance=pearson, rate=0.01):
    n = len(data)

    real_list = [[distance(data[i], data[j]) for j in range(n)]
                 for i in range(0, n)]

    outer_sum = 0.0
    loc = [[random.random(), random.random()] for i in range(n)]
    fake_dist = [[0.0 for j in range(n)] for i in range(n)]

    last_error = None
    for m in range(0, 3000):
        for i in range(n):
            for j in range(n):
                fake_dist[i][j] = sqrt(sum([pow(loc[i][x] - loc[j][x], 2)
                                            for x in range(len(loc[i]))]))

        grad = [[0.0, 0.0] for i in range(n)]

        total_error = 0
        for k in range(n):
            for j in range(n):
                if j == k:
                    continue
                error_term = (fake_dist[j][k] - real_list[j][k]) / real_list[j][k]
                grad[k][0] += ((loc[k][0] - loc[j][0]) / fake_dist[j][k]) * error_term
                grad[k][1] += ((loc[k][1] - loc[j][1]) / fake_dist[j][k]) * error_term

                total_error += abs(error_term)

        if last_error and last_error < total_error:
            break
        last_error = total_error

        for k in range(n):
            loc[k][0] -= rate * grad[k][0]
            loc[k][1] -= rate * grad[k][1]

    return loc


def draw_2d(data, labels, jpeg="md2d.jpg"):
    img = Image.new("RGB", (2000, 2000), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    for i in range(len(data)):
        x = (data[i][0] + 0.5) * 1000
        y = (data[i][1] + 0.5) * 1000
        font = ImageFont.truetype("/Library/Fonts/Arial Unicode.ttf", 14)
        draw.text((x, y), labels[i], (0, 0, 0), font=font)
    img.save(jpeg, "JPEG")


if __name__ == "__main__":
    article_names, words, data = readfile("article_data.txt")
    coor = scale_down(data)
    # print_clust(clust=clust, labels=article_names)
    # draw_den_drog_gram(clust, article_names, jpeg="zhihu_zhuanlan_clust.jpg")
    draw_2d(coor, labels=article_names)
