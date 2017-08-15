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
        out = flights[(origin, destination)][r[d]]
        ret = flights[(destination, origin)][r[d + 1]]
        print('%10%10s %5s - %5s $%3s %5s - %5s $%3s' % (
                                                    name,
                                                    origin,
                                                    out[0], out[1], out[2],
                                                    ret[0], ret[1], ret[2]))


def schedule_cost(sol):
    total_price = 0
    latest_arrival = 0
    earliest_dep = 24 * 60

    for d in range(len(sol) / 2):
        # Get inbound and outbound flights
        origin = people[d][1]
        outbound = flights[(origin, destination)][int(sol[d])]
        returnf = flights[(destination, origin)][int(sol[d+1])]

        # Total price is the price of all outbound and return flights
        total_price += outbound[2]
        total_price += returnf[2]

        # Track latest arrival and earliest departure
        if latest_arrival < get_minutes(outbound[1]):
            latest_arrival = get_minutes(outbound[1])
        if earliest_dep > get_minutes(returnf[0]):
            earliest_dep = get_minutes(returnf[0])

    total_wait = 0
    for d in range(len(sol) / 2):
        origin = people[d][1]
        outbound = flights[(origin, destination)][int(sol[d])]
        returnf = flights[(origin, destination)][int(sol[d+1])]
        total_wait += latest_arrival - get_minutes(outbound[1])
        total_wait += get_minutes(returnf[0]) - earliest_dep

        if latest_arrival > earliest_dep:
            total_price += 50

    return total_wait + total_price


if __name__ == '__main__':
    flights = build_dataset()
