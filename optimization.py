import time
import random
import math

people = [('Seymour', 'BOS'),
          ('Franny', 'DAL'),
          ('Zooey', 'CAK'),
          ('Walt', 'MIA'),
          ('Buddy', 'ORD'),
          ('Les', 'OMA')]

destination = 'LGA'


def build_dataset(filename='data/schedule.txt'):
    """ Creates flights dataset.
    """
    flight_data = {}
    with open(filename) as f:
        for line in f.readlines():
            origin, dest, depart, arrive, price = line.strip().split(',')
            flight_data.setdefault((origin, dest), [])
            flight_data[(origin, dest)].append((depart, arrive, int(price)))
    return flight_data


def get_minutes(tme):
    x = time.strptime(tme, '%H:%M')
    return x[3] * 60 + x[4]

def print_schedule(r):
    for d in range(len(r)):
        name = people[d][0]
        origin = people[d][1]
        out = flights[]

if __name__ == '__main__':
    flights = build_dataset()
