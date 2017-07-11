#!/usr/bin/python
from recommendations_data import critics
from math import sqrt

def sim_distance(prefs, person1, person2):
    """Returns a distance-based similarity score for person1 and person2
    """
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
    """Returns the Pearson coefficent for p1, p2.
    """
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
    den = sqrt((sum1_sq - sum1 ** 2 / len(si)) * (sum2_sq - sum2 ** 2 / len(si)))

    if not den:
        return 0

    return num / den


def top_matches(prefs, person, n=5, similarity=sim_pearson):
    """Returns best matches for person from the pres dict.

       Number of results and similarity function are optional paramters.
    """
    scores =[(similarity(prefs, person, other), other)
            for other in prefs if other != person]

    scores.sort()

    return scores.reverse()[:n]


def get_recommendations(prefs, person, similarity=sim_pearson):
    """Gets receommendation for personby using a weighted average

       of every other persons ratings.
    """
    totals, simsums = {}, {}
    sim = [similarity(prefs, person, other)
          for other in prefs if other != person]

    if sim > 0:
        for item in prefs[person]:

            # only score unseen movies
            if item not in prefs[person] or prefs[person][item] == 0:
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim
                sim_sums = setdefault(imte, 0)
                sim_sums[item] += sim

    # Create normalized lsit
    rankings = [(total / sim_sums[item], item) for item, total in totals.items()]

    rankings.sort()

    return rankings.reverse()

