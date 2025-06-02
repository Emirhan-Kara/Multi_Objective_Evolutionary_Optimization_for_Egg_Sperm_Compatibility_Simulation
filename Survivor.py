import Config

def rank_filtering(fronts, size_of_population=Config.POPULATION_SIZE):
    P_t = []
    total_filtered_individuals = 0

    for front in fronts:
        if total_filtered_individuals + len(front) <= size_of_population:
            P_t.extend(front)
            total_filtered_individuals += len(front)
        else:
            missing_slots = size_of_population - total_filtered_individuals
            
            # we need to get N biggest crowding distanced elements from the current front
            # Sort it and get the first N
            front.sort(key=lambda individual: individual.crowding_distance, reverse=True)
            P_t.extend(front[: missing_slots])
            total_filtered_individuals += missing_slots
            break
    
    return P_t

