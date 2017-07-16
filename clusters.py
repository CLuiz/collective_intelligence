from math import sqrt

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
