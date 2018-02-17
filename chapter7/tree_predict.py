from chapter7.config import my_data
from math import log
from pprint import pprint
from PIL import Image, ImageDraw


class DecisionNode:
    def __init__(self, col=-1, value=None, results=None, tb=None, fb=None):
        self.col = col
        self.value = value
        self.results = results
        self.tb = tb
        self.fb = fb


def divide_set(rows, column, value):
    if isinstance(value, int) or isinstance(value, float):
        split_function = lambda row: row[column] >= value
    else:
        split_function = lambda row: row[column] == value

    set1 = [row for row in rows if split_function(row)]
    set2 = [row for row in rows if not split_function(row)]
    return (set1, set2)


# 找出所有不可能的结果并返回一个字典
def unique_counts(rows):
    results = {}
    for row in rows:
        r = row[len(row) - 1]
        if r not in results:
            results[r] = 0
        results[r] += 1
    return results


# 基尼不纯度,得到的结果是某一行数据被随机分配到错误结果的总概率. 概率为0代表拆分的结果非常理想，说明每一行结果被分配在了正确的
# 集合中
def gini_impurity(rows):
    total = len(rows)
    counts = unique_counts(rows)
    imp = 0
    for k1 in counts:
        p1 = float(counts[k1]) / total
        for k2 in counts:
            if k1 == k2:
                continue
            p2 = float(counts[k2]) / total
            imp = p1 * p2
    return imp


# 第二种拆分方案，熵
def entropy(rows):
    log2 = lambda x: log(x) / log(2)
    results = unique_counts(rows)
    ent = 0.0
    for r in results.keys():
        p = float(results[r]) / len(rows)
        ent = ent - p * log2(p)
    return ent


def build_tree(rows, scoref=entropy):
    if len(rows) == 0:
        return DecisionNode()
    current_score = scoref(rows)

    # Set up some variables to track the best criteria
    best_gain = 0.0
    best_criteria = None
    best_sets = None

    column_count = len(rows[0]) - 1
    for col in range(0, column_count):
        # Generate the list of different values in
        # this column
        column_values = {}
        for row in rows:
            column_values[row[col]] = 1
        # Now try dividing the rows up for each value
        # in this column
        for value in column_values.keys():
            (set1, set2) = divide_set(rows, col, value)

            # Information gain
            p = float(len(set1)) / len(rows)
            gain = current_score - p * scoref(set1) - (1 - p) * scoref(set2)
            if gain > best_gain and len(set1) > 0 and len(set2) > 0:
                best_gain = gain
                best_criteria = (col, value)
                best_sets = (set1, set2)
    # Create the sub branches
    if best_gain > 0:
        trueBranch = build_tree(best_sets[0])
        falseBranch = build_tree(best_sets[1])
        return DecisionNode(col=best_criteria[0], value=best_criteria[1],
                            tb=trueBranch, fb=falseBranch)
    else:
        return DecisionNode(results=unique_counts(rows))


def print_tree(tree, indent=""):
    if tree.results:
        print(str(tree.results))
    else:
        print(str(tree.col) + ":" + str(tree.value) + "? ")
        print(indent + "T->", end="")
        print_tree(tree.tb, indent + " ")
        print(indent + "F->", end="")
        print_tree(tree.fb, indent + " ")


def get_width(tree):
    if not tree.tb and not tree.fb:
        return 1
    else:
        return get_width(tree.tb) + get_width(tree.fb)


# 分支的深度等于最长子分支的总长度加1
def get_depth(tree):
    if not tree.tb and not tree.fb:
        return 0
    else:
        return max(get_depth(tree.tb), get_depth(tree.fb)) + 1


def draw_tree(tree, jpeg="tree.jpg"):
    w = get_width(tree) * 100
    h = get_depth(tree) * 100 + 200

    img = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw_node(draw, tree, w / 2, 20)
    img.save(jpeg, "JPEG")


def draw_node(draw, tree, x, y):
    if not tree.results:
        w1 = get_width(tree.fb) * 100
        w2 = get_width(tree.tb) * 100

        left = x - (w1 + w2) / 2
        right = x + (w1 + w2) / 2

        draw.text((x - 20, y - 10), str(tree.col) + ":" + str(tree.value), (0, 0, 0))
        draw.line((x, y, left + w1 / 2, y + 100), fill=(255, 0, 0))
        draw.line((x, y, right - w2 / 2, y + 100), fill=(255, 0, 0))

        draw_node(draw, tree.fb, left + w1 / 2, y + 100)
        draw_node(draw, tree.tb, right - w2 / 2, y + 100)

    else:
        txt = " \n".join(["%s:%d" % v for v in tree.results.items()])
        draw.text((x - 20, y), txt, (0, 0, 0))


def classify(obeservation, tree):
    if tree.results:
        return tree.results
    else:
        v = obeservation[tree.col]
        branch = None
        if isinstance(v, int) or isinstance(v, float):
            if v >= tree.value:
                branch = tree.tb
            else:
                branch = tree.fb
        else:
            if v == tree.value:
                branch = tree.tb
            else:
                branch = tree.fb
        return classify(obeservation, branch)


if __name__ == "__main__":
    tree = build_tree(my_data)
    # print_tree(tree)
    # draw_tree(tree)
    print(classify(["(direct)", "USA", "yes", 5], tree))
