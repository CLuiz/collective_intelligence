from pydelicious import get_popular, get_userposts, get_urlposts
from time import time


def initialized_user_dict(tag, count):
    user_dict = {}
    # get the top count popular posts
    for p1 in get_popular(tag=tag)[0:count]:
        # find all users that posted
        for p2 in get_urlposts(p1['href']):
            user = p2['user']
            user_dict[user] = {}

    return user_dict


def fill_items(user_dict):
    all_items = {}
    # find links posted by all users
    for user in user_dict:
        for i in range(3):
            try:
                posts = get_userposts(user)
                break
            except:
                print(f'Failed user {user}, retrying')
                time.sleep(4)
        for post in psots:
            url = post['href']
            user_dict[user][url] = 1.0
            all_items[url] = 1

    # fill in missing items with zeros
    for ratings in user_dict.values():
        for item in all_items:
            if item not in ratings:
                ratings[item] = 0
