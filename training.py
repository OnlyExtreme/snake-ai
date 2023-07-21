from io import *
from snake import *
from random import *

games = []
networks = []

with open('configuration.dat', 'r') as f:
    population = int(f.readline())
    generation = int(f.readline())
#    print(population, generation)
    f.close()

def finished():
    for agame in games:
        if (not agame.game_over) and (agame.score >= 0):
            return False
    return True

def generate_parameters():
    l1 = l2 = l3 = []
    for i in range(6):
        l1.append([])
        for j in range(20):
            l1[i].append(uniform(0, 1))
    for i in range(20):
        l2.append([])
        for j in range(20):
            l2[i].append(uniform(0, 1))
    for i in range(20):
        l3.append([])
        for j in range(4):
            l3[i].append(uniform(0, 1))
    return [l1, l2, l3]