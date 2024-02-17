import random

def read_file(file_name):
    data = []

    with open(file_name, 'r') as file:
        num_test_cases = int(file.readline())
        for i in range(num_test_cases):
            num_data_points,degree = map(int, file.readline().strip().split())
            points = []
            for _ in range(num_data_points):
                x, y = map(float, file.readline().strip().split())
                points.append((x, y))

            data.append([degree, points])

    return data

def initialize_population (degree, num_population):
    population = []

    for _ in range(num_population):
        random_list = [random.uniform(-10, 10) for _ in range(degree+1)]
        population.append(random_list)

    return population

# Fitness function
def one_point_fitness (chromosome,point):
    fitness = chromosome[0]
    for i in range(1, len(chromosome)):
        fitness += pow(point[0], i)*chromosome[i]

    fitness = pow(fitness - point[1], 2)
    return fitness

def all_points_fitness (chromosome,points):
    total_error = 0
    for point in points:
        total_error += one_point_fitness(chromosome, point)

    total_error /= len(points)

    return total_error

def evaluate_fitness (population, points):
    fitness = []
    for chromosome in population:
        fitness.append(all_points_fitness(chromosome, points))

    return fitness

def select_parent (population,fitness):
    r1 = random.randint(0, len(population)-1)
    first_chromosome = population[r1].copy()
    fitness_first_chromosome = fitness[r1]

    # not same parent
    r2 = random.randint(0, len(population)-1)
    while r2 == r1:
        r2 = random.randint(0, len(population)-1)
    second_chromosome = population[r2].copy()
    fitness_second_chromosome = fitness[r2]

    if fitness_first_chromosome < fitness_second_chromosome:
        return first_chromosome
    else:
        return second_chromosome

def tournament_selection(population, fitness):
    mating_pool = []
    for _ in range(int(len(population)/2)):
        mating_pool.append(select_parent(population, fitness))

    return mating_pool

def filter (chromosome):
    for gene in chromosome:
        if gene < -10 or gene > 10:
            return False
    return True

def crossover (pc,parent1, parent2):
    r = random.random()
    if r <= pc:
        r1 = random.randint(1, len(parent1) - 1)
        r2 = random.randint(1, len(parent1) - 1)
        while r2 == r1:
            r2 = random.randint(1, len(parent1) - 1)
        r1, r2 = min(r1, r2), max(r1, r2)
        offspring1 = parent1[:r1] + parent2[r1:r2] + parent1[r2:]
        offspring2 = parent2[:r1] + parent1[r1:r2] + parent2[r2:]

    else:
        offspring1 = parent1
        offspring2 = parent2

    return offspring1, offspring2

def mutation (offspring, pm, lb, ub, t, T, b):
    for i in range(len(offspring)):
        rm = random.random()
        if rm <= pm:
            d_l = offspring[i] - lb
            d_u = ub - offspring[i]
            r1 = random.random()
            if r1 <= 0.5:
                y = d_l
                num = -1
            else:
                y = d_u
                num = 1
            r = random.random()
            d_t_y = y * (1 - pow(r, pow(1 - t / T, b)))
            offspring[i] += d_t_y*num

    return offspring


file_name = "curve_fitting_input.txt"
data = read_file(file_name)
index = 1
output_file = open("output.txt", 'w')
for x in data:
    print('Test Case Index:', index)
    output_file.write('Test Case Index: '+str(index)+'\n')
    index += 1
    degree, points = x[0], x[1]
    num_population = 250
    # initialization
    population = initialize_population(degree, num_population)
    num_generations = 500

    for t in range(1, num_generations+1):
        # sort fitness
        fitness = evaluate_fitness(population, points)
        combined_data = list(zip(population, fitness))
        sorted_combined_data = sorted(combined_data, key=lambda x: x[1])
        population, fitness = zip(*sorted_combined_data)
        # Tournament selection
        mating_pool = tournament_selection(population, fitness)

        offsprings = []
        num = 20

        for _ in range(num):
            r1 = random.randint(0, len(mating_pool) - 1)
            r2 = random.randint(0, len(mating_pool) - 1)
            while r2 == r1:
                r2 = random.randint(0, len(mating_pool) - 1)

            # crossover
            pc = 0.7
            offspring1, offspring2 = crossover(pc, mating_pool[r1], mating_pool[r2])
            # mutation
            pm = 0.05
            lb = -10
            ub = 10
            b = 1
            offspring1 = mutation(offspring1, pm, lb, ub, t, num_generations, b)
            offspring2 = mutation(offspring2, pm, lb, ub, t, num_generations, b)

            # infeasible solutions
            if not filter(offspring1):
                offspring1 = population[0].copy()

            if not filter(offspring2):
                offspring2 = population[0].copy()

            offsprings.append(offspring1)
            offsprings.append(offspring2)

        # replacement
        new_population = offsprings
        new_population += population[0:num_population-num*2]
        population = new_population.copy()

    fitness = evaluate_fitness(population, points)
    combined_data = list(zip(population, fitness))
    sorted_combined_data = sorted(combined_data, key=lambda x: x[1])
    population, fitness = zip(*sorted_combined_data)
    final_chromosome = population[0].copy()
    print('Coefficients:', final_chromosome)
    print('Mean Square Error:', fitness[0])
    print()
    output_file.write('Coefficients:'+ str(final_chromosome) + '\n')
    output_file.write('Mean Square Error: '+ str(fitness[0]) + '\n\n')