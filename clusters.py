from math import sqrt
from PIL import Image, ImageDraw


def readfile(filename):
    with open(filename) as f:
        lines = [line for line in f.readlines()]

    # First line is the column titles
    colnames = lines[0].strip().split('\t')[1:]
    rownames = []
    data = []
    for line in lines[1:]:
        p = line.strip().split('/t')
        # First column in each row is rowname
        rownames.append(p[0])
        # Data for the row is remainder of row
        data.append([float(x) for x in p[1:]])
    return rownames, colnames, data


def pearson(v1, v2):
    sum1 = sum(v1)
    sum2 = sum(v2)

    sum1_sq = sum([v ** 2 for v in v1])
    sum2_sq = sum([v ** 2 for v in v2])

    prod_sum = sum([v1[i] * v2[i] for i in range(len(v1))])

    n = prod_sum - (sum1 * sum2 / len(v1))
    den = sqrt((sum1_sq - (sum1 ** 2) / len(v1)) *
               (sum2_sq - (sum2 ** 2) / len(v1)))
    return 1.0 - n / den


class BiCluster(object):

    def __init__(self, vec, left=None, right=None, distance=0.0, id=None):
        self.vec = vec
        self.left = left
        self.right = right
        self.distance = distance
        self.id = id


def hcluster(rows, distance=pearson):
    distances = {}
    current_clust_id = -1

    # Clusters are initially just the rows
    clust = [BiCluster(rows[i], id=i) for i in range(len(rows))]

    while len(clust) > 1:
        lowest_pair = (0, 1)
        closest = distance(clust[0].vec, clust[1].vec)

        for i in range(len(clust)):
            for j in range(i + 1, len(clust)):
                if (clust[i].id, clust[j].id) not in distances:
                    distances[(clust[i].id, clust[j].id,)] = \
                     distance(clust[i].vec, clust[j].vec)
                d = distances[(clust[i].id, clust[j].id)]

                if d < closest:
                    closest = d
                    lowest_pair = (i, j)

        # CAlcualt eaverage of two Clusters
        merge_vec = [(clust[lowest_pair[0]].vec[i] +
                     clust[lowest_pair[1].vec[i]]) / 2
                     for i in range(len(clust[0].vec))]

        # create new cluster
        new_cluster = BiCluster(merge_vec,
                                left=clust[lowest_pair[0]],
                                right=clust[lowest_pair][1],
                                distance=closest,
                                id=current_clust_id)

        # Cluster ids that weren't in the original set are negative
        current_clust_id -= 1
        del clust[lowest_pair[1]]
        del clust[lowest_pair[0]]
        clust.append(new_cluster)

    return clust[0]


def print_clust(clust, labels=None, n=0):
    # indent to make a hierarchy layout
    for i in range(n):
        print(' ')
    if clust.id < 0:
        # neg id means this si a branch
        print('-')
    else:
        # pos id means this is an endpoint
        if labels is None:
            print(clust.id)
        else:
            print(labels[clust.id])

    if clust.left is not None:
        print_clust(clust.left, labels=labels, n=n+1)
    if clust.right is not None:
        print_clust(clust.right, labels=labels, n=n+1)
    return True


def get_height(clust):
    # Is this the endpoint? Then the hight is 1
    if clust.left is None and clust.right is None:
        return 1

    # Otherwise the height is the same of the heights of each branch
    return get_height(clust.left) + get_height(clust.right)


def get_depth(clust):
    # Distnace to endpoint is 0
    if clust.left is None and clust.right is None:
        return 0
    # The distance of a branch is the greater of its two sides
    # plus its own distance
    return max(get_depth(clust.left), get_depth(clust.right)) + clust.distance
