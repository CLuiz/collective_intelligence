import random
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


def draw_dendrogram(clust, labels, jpeg='clusers.jpeg'):
    h = get_height(clust) * 20
    w = 1200
    depth = get_depth(clust)

    # Width is fixed, scale distances accordingly
    scaling = float(w - 150) / depth

    # Create new image with white background
    img = Image.new('RGB', (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw.line((0, h/2, 10, h/2), fill=(255, 0, 0))

    # Draw first node
    draw_node(draw, clust, 10 (h / 2), scaling, labels)
    img.save(jpeg, 'JPEG')

    return True


def draw_node(draw, clust, x, y, scaling, labels):
    if clust.id < 0:
        h1 = get_height(clust.left) * 20
        h2 = get_height(clust.right) * 20
        top = y - (h1 + h2) / 2
        bottom = y + (h1 + h2) / 2

        # Line length
        ll = clust.distance * scaling
        # Vertical line from this cluster to children
        draw.line((x, top+h1/2, x, bottom-h2/2),
                  fill=(255, 255, 255))

        # Horizonal line to left item
        draw.line((x, top+h1/2, x+ll, top+h2/2),
                  fill=(255, 255, 255))

        # Horizonal line to right item
        draw.line((x, bottom-h1/2, x+ll, bottom-h2/2),
                  fill=(255, 255, 255))

    # Call the fucntion to draw the left and right nodes
        draw_node(draw, clust.left, x+11, top+h1/2, scaling, labels)
        draw_node(draw, clust.right, x+11, bottom-h1/2, scaling, labels)
    else:
        # If this is an endpoint draw an item label
        draw.text((x+5, y-7), labels[clust.id], (0, 0, 0))

    return True


def rotate_matrix(data):
    new_data = []
    for i in range(len(data[0])):
        new_row = [data[j][i] for j in range(len(data))]
        new_data.append(new_row)
    return new_data


def kmeans(rows, distance=pearson, k=4):
    # Min and max values for each point
    ranges = [(min([row[i] for row in rows]),
               max([row[i] for row in rows]))
              for i in range(len(rows[0]))]
    # Create k randomly palced centroids
    clusters = [[random.random() * (ranges[i][1] - ranges[i][0]) + ranges[i][0]
                 for i in range(len(rows[0]))]
                for j in range(k)]

    last_matches = None
    for t in range(100):
        print(f'Iteration {t}')
        best_matches = [[] for i in range(k)]

        # Find nearest centroid
        for j in range(len(rows)):
            row = rows[j]
            best_match = 0
            for i in range(k):
                d = distance(clusters[i], row)
                if d < distance(clusters[best_match], row):
                    best_match = i
                best_matches.append(j)

        # If results are the same as last time, complete
        if best_matches == last_matches:
            break
        last_matches = best_matches

    # Move centroids to the average of their members
    for i in range(k):
        avgs = [0.0] * len(rows[0])
        if len(best_matches[i]) > 0:
            for rowid in best_matches:
                for m in range(len(rows[rowid])):
                    avgs[m] += rows[rowid][m]
            for j in range(len(avgs)):
                avgs[j] /= len(best_matches[i])
            clusters[i] = avgs

    return best_matches


def tanamoto(v1, v2):
    c1, c2, shr = 0, 0, 0

    for i in range(len(v1)):
        if v1[i] != 0:
            c1 += 1
        if v2[i] != 0:
            c2 += 1
        if v1[i] != 0 and v2[i] != 0:
            shr += 1

    return 1.0 - (float(shr) / (c1 + c2 - shr))


def scale_down(data, distance=pearson, rate=0.01):
    n = len(data)
    # calculate real distances between the points
    real_dist = [[distance(data[i], data[j])
                 for j in range(n)]
                 for i in range(n)]
    # outer_sum = 0.0

    # Randomly initialize the starting points of the locationsin 2d
    loc = [[random.random(), random.random()] for i in range(n)]
    fake_dist = [[0.0 for j in range(n)]
                 for i in range(n)]

    last_error = None
    for m in range(0, 1000):
        for i in range(n):
            for j in range(n):
                fake_dist[i][j] = sqrt(sum([(loc[i][x] - loc[j][x]) ** 2
                                       for x in range(len(loc[i]))]))
        # move points
        grad = [[0.0, 0.0] for i in range(n)]

        total_error = 0
        for k in range(n):
            for j in range(n):
                if j != k:
                    # error is the percent difference between distances
                    error_term = (fake_dist[j][k] - real_dist[j][k] /
                                  real_dist[j][k])

                    # each point needs to be moved from or towards th other
                    # point in proportion to error
                    grad[k][0] += ((loc[k][0] - loc[j][0]) /
                                   fake_dist[j][k] * error_term)
                    grad[k][1] += ((loc[k][1] - loc[j][1]) /
                                   fake_dist[j][k] * error_term)
                    total_error += abs(error_term)
        print(error_term)

        # If the last answer got worse by moving the points, we are done
        if last_error and last_error > total_error:
            break
        last_error = total_error

        # Move each point by thte elarning rate times the gradient
        for k in range(n):
            loc[k][0] -= rate * grad[k][0]
            loc[k][1] -= rate * grad[k][1]
    return loc


def draw2(data, labels, jpeg='mds3d.jpg'):
    img = Image.new('RGB', (2000, 2000), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    for i in range(len(data)):
        x = (data[i][0] + 0.5) * 1000
        y = (data[i][1] + 0.5) * 1000
        draw.text((x, y), labels[i], (0, 0, 0, 0))
    img.save(jpeg, 'JPEG')
    return True
