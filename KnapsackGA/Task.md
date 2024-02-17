Write a genetic algorithm to solve the knapsack problem. 
You’ll be given an input file with the following format: 
• First line: Number of test cases (must be at least 1) 
For each test case: 
• Size of the knapsack 
• Number of items 
For each item: 
• Weight and value separated by space
1. Use a binary, one-dimensional chromosome. 
2. The population size and initialization method you use are up to you. You can actually try different population sizes to see how this will affect your results. The maximum number of generations is also up to you. 
3. Think about how you will handle infeasible solutions. Infeasible solutions are solutions that violate the constraints of the problem; therefore, they are not allowed. 
4. Use rank selection and one-point crossover. Choose the methods of mutation and replacement that you find appropriate. 
5. The output should consist of the test case index, the number of selected items, the total value, the total weight and the weight and value of each selected item.