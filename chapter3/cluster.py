from math import sqrt


def person(v1, v2):
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


def h_cluster(rows, distance=person):
    ditances = {}
    currentcluster_id = -1

