import random

def read_file(file_name):
    data = []

    with open(file_name, 'r') as file:
        num_test_cases = int(file.readline())

        for i in range(num_test_cases):
            file.readline()
            file.readline()
            size_knapsack = int(file.readline())
            num_items = int(file.readline())
            items = []
            for _ in range(num_items):
                weight, value = map(int, file.readline().strip().split())
                items.append((weight, value))

            data.append([size_knapsack, items])

    return data

def calculate_weight (chromosome,items):
    weight = 0
    for i in range(len(chromosome)):
        w, v = items[i][0], items[i][1]
        weight += chromosome[i]*w

    return weight

def filter (chromosome, size_knapsack, items):
    if calculate_weight(chromosome, items) > size_knapsack:
        return False
    return True

def initialize_population (size_knapsack, items, num_population):
    population = []

    for _ in range(num_population):
        random_list = [random.randint(0, 1) for _ in range(len(items))]
        while not filter(random_list, size_knapsack, items):
            random_list = [random.randint(0, 1) for _ in range(len(items))]
        population.append(random_list)

    return population

# Fitness function
def evaluate_fitness (chromosome,items):
    fitness = 0
    for i in range(len(chromosome)):
        w, v = items[i][0], items[i][1]
        fitness += chromosome[i]*v

    return fitness

def evaluate_all_fitness (population, items):
    all_fitness = []
    for chromosome in population:
        all_fitness.append(evaluate_fitness(chromosome, items))

    return all_fitness

def calculate_probabilities (n):
    probabilities = []
    sum = n*(n+1)/2
    for i in range(1,n+1):
        probabilities.append(i/sum)

    return probabilities

def calculate_cumulative (probabilities):
    cumulative_fitness = []
    lower = 0
    for p in probabilities:
        cumulative_fitness.append([lower, p+lower])
        lower += p

    return cumulative_fitness

def find_parent_num (r, cumulative_fitness):
    parent = -1
    for i in range(len(cumulative_fitness)):
        if i == len(cumulative_fitness)-1:
            if (cumulative_fitness[i][0] <= r <= cumulative_fitness[i][1]):
                parent = i
                break
        else:
            if (cumulative_fitness[i][0] <= r < cumulative_fitness[i][1]):
                parent = i
                break

    return parent

def select_parent (cumulative_fitness):
    r1 = random.random()
    first_parent = find_parent_num(r1, cumulative_fitness)

    # not same parent
    r2 = random.random()
    second_parent = find_parent_num(r2, cumulative_fitness)
    while second_parent == first_parent:
        r2 = random.random()
        second_parent = find_parent_num(r2, cumulative_fitness)

    return first_parent, second_parent

def crossover (first_parent, second_parent, pc):
    xc = random.randint(1, len(first_parent)-1)
    rc = random.random()

    if rc <= pc:
        offspring1 = first_parent[:xc] + second_parent[xc:]
        offspring2 = second_parent[:xc] + first_parent[xc:]
    else:
        offspring1 = first_parent
        offspring2 = second_parent


    return offspring1, offspring2

def mutation (offspring):
    r1 = random.randint(0, len(offspring)-1)
    r2 = random.randint(0, len(offspring) - 1)
    while r2 == r1:
        r2 = random.randint(0, len(offspring) - 1)
    offspring[r1], offspring[r2] = offspring[r2], offspring[r1]
    return offspring

def find_best_fitness (all_fitness):
    max_e= max(all_fitness)
    max_ind = all_fitness.index(max_e)
    return max_ind


file_name = "knapsack_input.txt"
data = read_file(file_name)
index = 1
output_file = open("output.txt", 'w')
for x in data:
    print('Test Case Index:', index)
    index += 1
    size_knapsack, items = x[0], x[1]
    num_population = 100
    # initialization
    population = initialize_population(size_knapsack, items, num_population)
    num_generations = 500

    for _ in range(num_generations):
        # sort fitness
        all_fitness = evaluate_all_fitness(population, items)
        combined_data = list(zip(population, all_fitness))
        sorted_combined_data = sorted(combined_data, key=lambda x: x[1])
        population, all_fitness = zip(*sorted_combined_data)

        # rank selection
        probabilities = calculate_probabilities(len(all_fitness))
        cumulative = calculate_cumulative(probabilities)

        # one-point crossover
        first_parent_num, second_parent_num = select_parent(cumulative)
        pc = 0.6
        first_parent = population[first_parent_num].copy()
        second_parent = population[second_parent_num].copy()
        offspring1, offspring2 = crossover(first_parent, second_parent, pc)

        # mutation
        offspring1 = mutation(offspring1)
        offspring2 = mutation(offspring2)

        # infeasible solutions
        if not filter(offspring1, size_knapsack, items):
            offspring1 = population[find_best_fitness(all_fitness)].copy()

        if not filter(offspring2, size_knapsack, items):
            offspring2 = population[find_best_fitness(all_fitness)].copy()

        # replacement
        new_population = [offspring1, offspring2]
        new_population += population[2:num_population]

        population = new_population.copy()

    # sort fitness
    all_fitness = evaluate_all_fitness(population, items)
    combined_data = list(zip(population, all_fitness))
    sorted_combined_data = sorted(combined_data, key=lambda x: x[1])
    population, all_fitness = zip(*sorted_combined_data)

    # output
    final_chromosome = population[num_population - 1].copy()
    print('Number of Selected Items:', final_chromosome.count(1))
    output_file.write('Number of Selected Items: '+ str(final_chromosome.count(1))+'\n')
    print('Total Value:', evaluate_fitness(final_chromosome, items))
    output_file.write('Total Value: '+ str(evaluate_fitness(final_chromosome, items))+'\n')
    print('Total Weight:', calculate_weight(final_chromosome, items))
    output_file.write('Total Weight: '+ str(calculate_weight(final_chromosome, items))+'\n')
    i = 1
    for x in range(len(final_chromosome)):
        if final_chromosome[x] == 1:
            print("Item", i, " Weight =", items[x][0], " Value =", items[x][1])
            output_file.write("Item "+ str(i)+ " Weight = "+ str(items[x][0])+ "  Value = "+ str(items[x][1])+'\n')

            i += 1

    print('-'*50)
    output_file.write('-'*70+'\n')
