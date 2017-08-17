#!/usr/bin/python

from recommendations_data import critics
from math import sqrt


def sim_distance(prefs, person1, person2):
    """Returns a distance-based similarity score for person1 and person2."""
    # Get dict of shared items
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1

    # if they have no ratings in common return 0
    if not si:
        return 0

    # Add up the squares of all the differences
    sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2)
                         for item in prefs[person1] if item in prefs[person2]])

    return 1 / (1 + sum_of_squares)


def sim_pearson(prefs, p1, p2):
    """Returns the Pearson coefficent for p1, p2."""
    # Get dict of mutually rated items
    si = {k: 1 for k in prefs[p1] if k in prefs[p2]}

    if not si:
        return 0

    # Add up all preferences
    sum1 = sum([prefs[p1][item] for item in si])
    sum2 = sum([prefs[p2][item] for item in si])

    # Sum up the squares
    sum1_sq = sum([prefs[p1][item] ** 2 for item in si])
    sum2_sq = sum([prefs[p2][item] ** 2 for item in si])

    # Sum products
    sum_prod = sum([prefs[p1][item] * prefs[p2][item] for item in si])

    # Calculate Pearson score
    num = sum_prod - (sum1 * sum2 / len(si))
    den = sqrt((sum1_sq - sum1 ** 2 /
                len(si)) * (sum2_sq - sum2 ** 2 / len(si)))

    if not den:
        return 0

    return num / den


def top_matches(prefs, person, n=5, similarity=sim_pearson):
    """Returns best matches for person from the pres dict.
       Number of results and similarity function are optional paramters.
    """
    scores = [(similarity(prefs, person, other), other)
              for other in prefs if other != person]

    scores.sort()

    return scores.reverse()[:n]


def get_recommendations(prefs, person, similarity=sim_pearson):
    """Gets receommendation for personby using a weighted average
       of every other persons ratings.
    """
    totals, sim_sums = {}, {}
    sim = [similarity(prefs, person, other)
           for other in prefs if other != person]
    for other in prefs:
        if other == person:
            continue

        if sim > 0:
            for item in prefs[person]:

                # only score unseen movies
                if item not in prefs[person] or prefs[person][item] == 0:
                    totals.setdefault(item, 0)
                    totals[item] += prefs[other][item] * sim
                    sim_sums.setdefault(item, 0)
                    sim_sums[item] += sim

    # Create normalized lsit
    rankings = [(total / sim_sums[item], item)
                for item, total in totals.items()]

    rankings.sort()

    return rankings.reverse()


def transform_prefs(prefs):
    result = {}

    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})
            result[item][person] = prefs[person][item]
    return result


def calculate_similar_items(prefs, n=10):
    """Create a dict of items showing which items
       they are most similar to.
    """
    result = {}

    # Invert perference matrix to be item-centric
    item_prefs = transform_prefs(prefs)
    c = 0
    for item in item_prefs:
        c += 1
        if c % 100 == 0:
            print(f'{c / len(item_prefs)}')
        # Find most similar items
        result[item] = top_matches(item_prefs,
                                   item,
                                   n=n,
                                   similarity=sim_distance)
    return result


def get_recommended_items(prefs, item_match, user):
    user_ratings, scores, total_sim = ({} for i in range(3))

    # loop over all items rated by this user
    for (item, rating) in user_ratings.items():

        # Loop over similar items
        for (similarity, item2) in item_match[item]:

            # Ignore if user has previously rated item
            if item2 in user_ratings:
                continue

            # Calculate weighted sum of rating times similarity
            scores.setdefault(item2, 0)
            scores[item2] += similarity * rating

            # Sum similarities
            total_sim = setdefault(item2, 0)
            total_sim[item2] += similarity

    # Divide each total score by total weighting to get an average
    rankings = [(score / total_sim[item], item)
                for item, score in scores.items()]

    # Return rankings from highest to lowest
    return rankings.sort().reverse()


def load_movie_lens(path='/data/movielens'):
    movies = {}
    # Get movie titles
    for line in open(path + '/u.item'):
        (id, title) = line.split('|')[:2]
        movies[id] = title

    # Load data
    prefs = {}
    for line in open(path + '/u.data'):
        (user, movieid, rating, ts) = line.split('/t')
        prefs.setdefault(user, {})
        prefs[user][movies[movieid]] = float(rating)
    return prefs
