import random

from Config import *

def is_feasible(individual):
    return individual.objectives[0] >= CONSTRAINT

def is_individual_1_winning(individual_1, individual_2):
    """
    Tournament selection with feasibility preference:
    - Feasible individuals are always preferred over infeasible ones.
    - Among feasible ones: use rank and crowding distance.
    """
    feasible_1 = is_feasible(individual_1)
    feasible_2 = is_feasible(individual_2)

    if feasible_1 and not feasible_2:
        return True
    if not feasible_1 and feasible_2:
        return False

    if (individual_1.rank < individual_2.rank) or (
        individual_1.rank == individual_2.rank and individual_1.crowding_distance > individual_2.crowding_distance):
        return True
    return False


def crowded_tournament_selection(population, mating_pool_size=MATING_POOL_SIZE):
    M_t = []

    while len(M_t) < mating_pool_size:
        # Randomly select two individuals from the population
        i1 = random.randint(0, len(population) - 1)
        i2 = random.randint(0, len(population) - 1)
        while i2 == i1:
            i2 = random.randint(0, len(population) - 1)

        if is_individual_1_winning(population[i1], population[i2]):
            M_t.append(population[i1])
        else:
            M_t.append(population[i2])

    return M_t

