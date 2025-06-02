import Config
from Sperm import Sperm
from Egg import Egg

def dominates(individual_1, individual_2):
    """ Check if individual_1 dominates individual_2 """
    at_least_one_better = False
    
    for i in range(Config.OBJECTIVE_NUM):
        obj1 = individual_1.objectives[i]
        obj2 = individual_2.objectives[i]

        if Config.IS_MINIMIZATION_OBJECTIVE[i]:
            # Minimization objective
            if obj1 > obj2:  # individual_1 is worse
                return False
            elif obj1 < obj2:  # individual_1 is better
                at_least_one_better = True
        else:
            # Maximization objective
            if obj1 < obj2:  # individual_1 is worse
                return False
            elif obj1 > obj2:  # individual_1 is better
                at_least_one_better = True
    
    return at_least_one_better
         
def get_nondominated_set(population, rank, hashset=set()):
    """
        This method gets the non-dominated set (pareto front) from the population

        O(n^2 * m) time n=pop_size  m=# of objcetives
    """
    nondominated_set = []
    indexes = []

    for i in range(len(population)):
        if i in hashset:
            continue

        is_dominated = False
        for j in range(len(population)):
            if i == j or j in hashset:
                continue

            # If the individual is being dominated, skip it
            if dominates(population[j], population[i]):
                is_dominated = True
                break
        
        if not is_dominated:
            population[i].rank = rank
            nondominated_set.append(population[i])
            indexes.append(i)

    return nondominated_set, indexes

def nondominated_sorting(population):
    """
        This function performs non-dominated sorting
        Ranks are assigned to each individual within the population
        Based on the ranks, fronts are seperated
        It returns the seperated fronts

        O(n) space, n=population size
        O(n^3 * m) time, n=pop_size  m=# of objcetives
    """
    hashset = set()     # To exclude the previous ranks (better fronts)
    rank = 1            # Rank index
    fronts = []         # To hold each front

    while not (len(hashset) == len(population)):
        nondominated_set, indexes = get_nondominated_set(population, rank, hashset) # n^2 time
        hashset.update(indexes)
        rank += 1
        fronts.append(nondominated_set)

    return fronts

def crowding_distance_evaluation(population):
    """
        O(n) space, n=population size
        O(n^3 * m) time, n=pop_size  m=# of objcetives
    """
    # Divide the population into different fronts
    fronts = nondominated_sorting(population)

    # Get the max and min values for all the objectives
    obj_maxes = []
    obj_mins = []
    for i in range(Config.OBJECTIVE_NUM):
        obj_maxes.append(max(individual.objectives[i] for individual in population))
        obj_mins.append(min(individual.objectives[i] for individual in population))

    # For each front, calculate crowding distances
    for front in fronts:
        # If there are less than 3 individuals in the front, all of their crowding distance is infinite
        if len(front) < 3:
            for individual in front:
                individual.crowding_distance = float('inf')
            continue

        # Initialize crowding distances to 0
        for individual in front:
            individual.crowding_distance = 0.0

        for i in range(Config.OBJECTIVE_NUM):
            # Sort the front based on the corresponding objective
            front.sort(key=lambda individual: individual.objectives[i])

            # First and last elements have infinite crowding distance
            front[0].crowding_distance = float('inf')
            front[-1].crowding_distance = float('inf')

            for k in range (1, len(front) - 1):
                if obj_maxes[i] != obj_mins[i]:
                    front[k].crowding_distance += ((front[k+1].objectives[i] - front[k-1].objectives[i]) / (obj_maxes[i] - obj_mins[i]))

    return fronts



def evaluate_population(population, egg: Egg, generation_number=1):
    for individual in population:
        individual.evaluate_objectives(egg, generation_number)

    return crowding_distance_evaluation(population)


    