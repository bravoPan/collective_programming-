from math import sqrt
from pprint import pprint
from PIL import Image, ImageDraw, ImageFont


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
    h = get_depth(clust) * 240
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
        draw.text((x + 15, y - 7), labels[clust.id], (0, 0, 0), font=font)


if __name__ == "__main__":
    #
    article_names, words, data = readfile("article_data.txt")
    # pprint(article_names)
    clust = h_cluster(data)
    # print_clust(clust, labels=article_names)
    draw_den_drog_gram(clust, article_names, jpeg="article_clust.jpg")
