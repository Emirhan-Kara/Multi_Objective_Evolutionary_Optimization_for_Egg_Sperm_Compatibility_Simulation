import random
import Config

def create_parent_pairs(mating_pool):
    # Shuffle the pool and pair the individuals
    random.shuffle(mating_pool)
    
    pairs = []
    for i in range(0, len(mating_pool)-1, 2):
        pairs.append((mating_pool[i], mating_pool[i+1]))
        
    return pairs

# ==================================================================================================================================

def sbx_calculate(p1, p2, min_val, max_val, eta):
        if abs(p1 - p2) < 1e-10:
            return p1, p2

        if p1 > p2:
            p1, p2 = p2, p1

        k = random.random()
        if k <= 0.5:
            beta = (2.0 * k) ** (1.0 / (eta + 1.0))
        else:
            beta = (1.0 / (2.0 * (1.0 - k))) ** (1.0 / (eta + 1.0))

        c1 = 0.5 * ((p1 + p2) - beta * (p2 - p1))
        c2 = 0.5 * ((p1 + p2) + beta * (p2 - p1))

        c1 = max(min(c1, max_val), min_val)
        c2 = max(min(c2, max_val), min_val)
        return c1, c2

def sbx_crossover(parent1, parent2, eta=Config.eta):
    # Create child sperm instances
    child1 = parent1.copy()
    child2 = parent2.copy()

    # Apply SBX to resource allocation
    child1.genetic_resources, child2.genetic_resources = sbx_calculate(
        parent1.genetic_resources, parent2.genetic_resources, 10, 90, eta
    )
    child1.biological_resources = child1.total_resources - child1.genetic_resources
    child2.biological_resources = child2.total_resources - child2.genetic_resources
    
    # Apply SBX to pH tolerance (only parameter not dependent on resources)
    child1.ph_tolerance, child2.ph_tolerance = sbx_calculate(
        parent1.ph_tolerance, parent2.ph_tolerance, 6.5, 8.5, eta
    )
    
    # Recalculate dependent parameters based on new resource allocation
    recalculate_resource_dependent_parameters(child1)
    recalculate_resource_dependent_parameters(child2)
    
    # Handle HLA profiles - size depends on genetic resources
    crossover_hla_profiles(child1, parent1, parent2)
    crossover_hla_profiles(child2, parent2, parent1)

    return child1, child2

def recalculate_resource_dependent_parameters(sperm):
    """Recalculate biological parameters based on resource allocation"""
    resource_factor = sperm.biological_resources / 100
    
    # Recalculate biological parameters with some randomness
    base_dfi = random.uniform(0, 50)
    base_motility = random.uniform(30, 100)
    base_morphology = random.uniform(10, 100)
    base_velocity = random.uniform(10, 100)
    
    sperm.dfi = base_dfi * (2 - resource_factor)  # Less resources = more damage
    sperm.motility = base_motility * resource_factor
    sperm.morphology = base_morphology * resource_factor
    sperm.velocity = base_velocity * resource_factor

def crossover_hla_profiles(child, parent1, parent2):
    """Crossover HLA profiles considering genetic resource constraints"""
    # Calculate max HLA size based on genetic resources
    max_hla = min(6, max(2, int(child.genetic_resources / 15)))
    
    # Combine parent HLA profiles
    combined_hla = list(set(parent1.hla_profile + parent2.hla_profile))
    
    if len(combined_hla) <= max_hla:
        child.hla_profile = combined_hla
    else:
        # Randomly select from combined pool
        child.hla_profile = random.sample(combined_hla, max_hla)

# ==================================================================================================================================

def mutate_value(value, min_val, max_val, delta, mutation_rate):
    if random.random() < mutation_rate:
        r = random.random()
        y = value + delta * (r - 0.5)
        return max(min(y, max_val), min_val)
    return value

def modified_random_mutation(sperm, mutation_rate=Config.MUTATION_RATE, delta=Config.delta):
    """Mutation for resource-based sperm"""
    
    # Mutate resource allocation
    old_genetic_resources = sperm.genetic_resources
    sperm.genetic_resources = mutate_value(
        sperm.genetic_resources, 10, 90, delta, mutation_rate
    )
    
    # If resources changed, update biological resources and dependent parameters
    if old_genetic_resources != sperm.genetic_resources:
        sperm.biological_resources = sperm.total_resources - sperm.genetic_resources
        recalculate_resource_dependent_parameters(sperm)
        
        # Adjust HLA profile size if needed
        max_hla = min(6, max(2, int(sperm.genetic_resources / 15)))
        if len(sperm.hla_profile) > max_hla:
            # Remove excess alleles
            sperm.hla_profile = random.sample(sperm.hla_profile, max_hla)
        elif len(sperm.hla_profile) < max_hla and random.random() < mutation_rate:
            # Add new alleles if possible
            possible_alleles = list(set(Config.HLA_ALLELES) - set(sperm.hla_profile))
            if possible_alleles and len(sperm.hla_profile) < max_hla:
                added = random.choice(possible_alleles)
                sperm.hla_profile.append(added)
    
    # Mutate pH tolerance
    sperm.ph_tolerance = mutate_value(sperm.ph_tolerance, 6.5, 8.5, delta/40.0, mutation_rate)
    
    # Small mutations to biological parameters (within resource constraints)
    if random.random() < mutation_rate:
        noise_factor = 1 + (random.random() - 0.5) * 0.1  # +-5% noise
        resource_factor = sperm.biological_resources / 100
        
        sperm.dfi = max(0, min(50, sperm.dfi * noise_factor))
        sperm.motility = max(30 * resource_factor, min(100 * resource_factor, sperm.motility * noise_factor))
        sperm.morphology = max(10 * resource_factor, min(100 * resource_factor, sperm.morphology * noise_factor))
        sperm.velocity = max(10 * resource_factor, min(100 * resource_factor, sperm.velocity * noise_factor))
    
    # HLA mutation (within genetic resource constraints)
    if random.random() < mutation_rate:
        max_hla = min(6, max(2, int(sperm.genetic_resources / 15)))
        
        if len(sperm.hla_profile) > 2 and random.random() < 0.5:
            # Remove one allele
            removed = random.choice(sperm.hla_profile)
            sperm.hla_profile.remove(removed)
        elif len(sperm.hla_profile) < max_hla:
            # Add one new allele not already in profile
            possible_alleles = list(set(Config.HLA_ALLELES) - set(sperm.hla_profile))
            if possible_alleles:
                added = random.choice(possible_alleles)
                sperm.hla_profile.append(added)

# ==================================================================================================================================

def crossover_and_mutation(parent1, parent2, crossover_rate=Config.CROSSOVER_RATE, mutation_rate=Config.MUTATION_RATE):

    if random.random() < crossover_rate:
        child1, child2 = sbx_crossover(parent1, parent2)
        modified_random_mutation(child1, mutation_rate)
        modified_random_mutation(child2, mutation_rate)
    else:
        child1 = parent1.copy()
        child2 = parent2.copy()
        modified_random_mutation(child1, mutation_rate)
        modified_random_mutation(child2, mutation_rate)

    return child1, child2

def variation(mating_pool, crossover_rate=Config.CROSSOVER_RATE, mutation_rate=Config.MUTATION_RATE):
    Q_t = []
    
    parent_pairs = create_parent_pairs(mating_pool)

    for parent1, parent2 in parent_pairs:
        child1, child2 = crossover_and_mutation(parent1, parent2, crossover_rate, mutation_rate)
        Q_t.append(child1)
        Q_t.append(child2)

    return Q_t