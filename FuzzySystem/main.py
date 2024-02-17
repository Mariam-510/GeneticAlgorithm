import re


class FuzzySystem:
    def __init__(self):
        self.name = ''
        self.description = ''
        self.variables = []
        self.rules = []

    def create_system(self, name, description):
        self.name = name
        self.description = description

    def add_variable(self, variable):
        self.variables.append(variable)

    def add_rule(self, rule):
        self.rules.append(rule)


class Variable:
    def __init__(self, name, var_type, lower, upper):
        self.name = name
        self.type = var_type
        self.lower = lower
        self.upper = upper
        self.fuzzy_sets = []
        self.crisp_value = 0

    def set_fuzzy_set(self, fuzzy_set):
        self.fuzzy_sets.append(fuzzy_set)


class FuzzySet:
    def __init__(self, name, type, values):
        self.name = name
        self.type = type
        self.values = values


class Rule:
    def __init__(self, vars, sets,operators, outVar, outSet, str):
        self.vars = vars
        self.sets = sets
        self.operators = operators
        self.outVar = outVar
        self.outSet = outSet
        self.str = str


def validate_var_range(lower, upper):
    return 0 <= lower <= upper <= 100

# Function to check if specified variable and fuzzy set exists in the fuzzy system
def checkRule(fuzzySystem,var,set,type):
    for variable in fuzzySystem.variables:
        if variable.name == var:
            if variable.type != type:
                return False
            else:
                for fuzzySet in variable.fuzzy_sets:
                    if fuzzySet.name == set:
                        return True
    return False

def checkExistRule(rules,input_rule):
    for rule in rules:
        if rule.str.replace(' ','') == input_rule.str.replace(' ',''):
            return True
    return False

# Function to check if all fuzzy sets are not empty for each variable in fuzzy system
def checkFuzzySets(fuzzySystem):
    for variable in fuzzySystem.variables:
        if len(variable.fuzzy_sets) == 0:
            return False
    return True

# Function to check if the fuzzy system is ready for simulation by checking variables, fuzzy sets, and rules not empty
def checkFuzzySystem(fuzzySystem):
    if len(fuzzySystem.variables) == 0:
        print('CAN’T START THE SIMULATION! Please add the variables, the fuzzy sets, and rules first.')
        return False
    elif not checkFuzzySets(fuzzySystem):
        print('CAN’T START THE SIMULATION! Please add the fuzzy sets and rules first')
        return False
    elif len(fuzzySystem.rules) == 0:
        print('CAN’T START THE SIMULATION! Please add rules first')
        return False

    return True

# Function to select fuzzy sets that crisp value is between their range
def selectFuzzySets(variable):
    fuzzysets = []
    for fuzzySet in variable.fuzzy_sets:  # ex (exp_level=40) -> (intermediate, expert)
        if fuzzySet.values[0] <= variable.crisp_value < fuzzySet.values[len(fuzzySet.values)-1]:
            fuzzysets.append(fuzzySet)

    return fuzzysets

# Function to determine the points of intersection for a given fuzzy set and crisp value
def linePoints(fuzzyset,variable):
    points = []
    for i in range(len(fuzzyset.values)-1):
        if fuzzyset.values[i] <= variable.crisp_value < fuzzyset.values[i+1]:
            if len(fuzzyset.values) == 3:
                if i == 0:
                    points.append((fuzzyset.values[i], 0))
                    points.append((fuzzyset.values[i+1], 1))
                elif i == 1:
                    points.append((fuzzyset.values[i], 1))
                    points.append((fuzzyset.values[i+1], 0))
            else:
                if i == 0:
                    points.append((fuzzyset.values[i], 0))
                    points.append((fuzzyset.values[i+1], 1))
                elif i == 1:
                    points.append((fuzzyset.values[i], 1))
                    points.append((fuzzyset.values[i+1], 1))
                elif i == 2:
                    points.append((fuzzyset.values[i], 1))
                    points.append((fuzzyset.values[i+1], 0))
            break
    return points

# Function to calculate the degree of membership for a given crisp value and points of line using line equation
def degreeMemberShip(x, points):  # ex points = [[30,1], [45,0]]
    slope = (points[1][1] - points[0][1]) / (points[1][0] - points[0][0])
    b = points[0][1] - slope*points[0][0]
    y = slope * x + b
    return y

# Function for fuzzification of IN variables, determining degree of membership for intersected fuzzy sets.
def fuzzification(fuzzySystem):
    degree_member_ship = []
    for variable in fuzzySystem.variables:
        if variable.type == 'IN':
            fuzzysets = selectFuzzySets(variable)  # ex (exp_level=40) -> (intermediate, expert)
            for fuzzyset in fuzzysets:
                points = linePoints(fuzzyset, variable) # ex points = [[30,1], [45,0]]
                y = degreeMemberShip(variable.crisp_value, points)
                # ex [{'variable': exp_level, 'fuzzySet': intermediate, 'value': }]
                degree_member_ship.append({'variable':variable.name,'fuzzySet':fuzzyset.name, 'value': y})

    return degree_member_ship

def check(operators,op):
    if any(oper == op for oper in operators):
        return True
    else:
        return False

def applyRule(vars,operators):
    while check(operators, 'and_not') or check(operators, 'or_not'):
        for i in range(len(operators)):
            if operators[i] == 'and_not':
                vars[i+1] = 1-vars[i+1]
                operators[i] = 'and'
                break
            elif operators[i] == 'or_not':
                vars[i+1] = 1-vars[i+1]
                operators[i] = 'or'
                break
    while check(operators,'and'):
        for i in range(len(operators)):
            if operators[i] == 'and':
                num = min(vars[i], vars[i+1])
                del operators[i]
                del vars[i]
                del vars[i]
                vars.insert(i,num)
                break

    while check(operators,'or'):
        for i in range(len(operators)):
            if operators[i] == 'or':
                num = max(vars[i], vars[i+1])
                del operators[i]
                del vars[i]
                del vars[i]
                vars.insert(i,num)
                break

    return vars[0]

# Function for applying the rules
def Inference(degree_member_ship, fuzzySystem):
    inferences = []
    for rule in fuzzySystem.rules:
        v = [0 for _ in range(len(rule.vars))]
        for d in degree_member_ship:
            for i in range(len(rule.vars)):
                if d['variable'] == rule.vars[i] and d['fuzzySet'] == rule.sets[i]:
                    v[i] = d['value']
        operators_temp = rule.operators.copy()
        value = applyRule(v, operators_temp)
        inference = [rule.outVar, rule.outSet, value]
        inferences.append(inference)  # ['risk', 'low', '0.3']
    return inferences

# Function to calculate the centroid of each fuzzy set for defuzzification (sum of values/num of values)
def centroid(variable):
    centroids = []  # low = (0+25+50)/3 = 37.5
    for fuzzySet in variable.fuzzy_sets: # {'fuzzySetName':low, 'centroid':37.5}
         centroids.append({'fuzzySetName':fuzzySet.name,'centroid':sum(fuzzySet.values)/len(fuzzySet.values)})

    return centroids

# Function for defuzzification, determining the crisp output values.
def defuzzification(inferences, fuzzySystem):
    for variable in fuzzySystem.variables:
        if variable.type == 'OUT': # risk
            v1, v2 = 0, 0
            cen = centroid(variable)  # [{'fuzzySetName':low, 'centroid':37.5}, {'fuzzySetName':high,'centroid':50},...]
            for inference in inferences:  # [['risk', 'low', '0.3'],['risk', 'high', '0'],...]
                if inference[0] == variable.name:
                    for c in cen:
                        if c['fuzzySetName'] == inference[1]:
                            v1 += c['centroid']*inference[2]
                            v2 += inference[2]

            if v2 != 0:
                variable.crisp_value = v1/v2
            else:
                variable.crisp_value = 0
    return fuzzySystem


def main_menu():
    fuzzy_system = FuzzySystem()
    print("\nFuzzy Logic Toolbox")
    print("===================")

    while True:
        print("1- Create a new fuzzy system")
        print("2- Quit\n")

        choice = input()

        if choice == '1':
            print("\nEnter the system’s name and a brief description:")
            print("-------------------------------------------------")
            name = input()
            description = ''
            while True:
                chunk = input()
                if not chunk:
                    break
                description += chunk
            fuzzy_system.create_system(name, description)
            system_menu(fuzzy_system)

        elif choice == '2':
            exit()

        else:
            print('Invalid Input\n')


def system_menu(fuzzy_system):
    while True:
        print("\nMain Menu:")
        print("==========")
        print("1- Add variables.")
        print("2- Add fuzzy sets to an existing variable.")
        print("3- Add rules.")
        print("4- Run the simulation on crisp values.")
        print("")

        choice = input()

        if choice == '1':
            print("Enter the variable’s name, type (IN/OUT), and range ([lower, upper]): (Press x to finish)")
            print("--------------------------------------------------------------------")
            while True:
                variable_info = input()

                if variable_info == 'x':
                    break

                # Define the pattern for matching input
                pattern = re.compile(r'^\s*(\w+)\s+(IN|OUT)\s+\[\s*(\d+)\s*,\s*(\d+)\s*\]\s*$')

                # Match the input against the pattern
                match = pattern.match(variable_info)

                if not match:
                    print("Invalid input format. Please enter the correct format.")
                    continue

                name, var_type, lower, upper = match.groups()

                # Convert lower and upper to integers
                lower, upper = int(lower), int(upper)

                # Validate range
                if not validate_var_range(lower, upper):
                    print("Invalid input. Please enter a valid range ([lower, upper]).")
                    continue

                # Check if the variable already exists
                if any(existing_variable.name == name for existing_variable in fuzzy_system.variables):
                    print(f"Variable '{name}' already exists. Please enter a unique variable name.")
                    continue

                # Create and add the variable to the fuzzy system
                variable = Variable(name, var_type, lower, upper)
                fuzzy_system.add_variable(variable)

        elif choice == '2':
            print("\nEnter the variable’s name: ")
            print("--------------------------")
            var_name = input()
            if any(existing_variable.name == var_name for existing_variable in fuzzy_system.variables):
                for variable in fuzzy_system.variables:
                    if variable.name == var_name:
                        print("\nEnter the fuzzy set name, type (TRI/TRAP) and values: (Press x to finish)")
                        print("-------------------------------------------------------------------------")
                        while True:
                            fuzzy_set_info = input()
                            if fuzzy_set_info == 'x':
                                break

                            pattern = re.compile(r'^\s*(\w+)\s+(TRI|TRAP)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*(?:([\d.]+)\s*)?$')

                            match = pattern.match(fuzzy_set_info)

                            if not match:
                                print("Invalid input format. Please enter the correct format.")
                                continue

                            fuzzy_set_name, fuzzy_set_type, *fuzzy_set_values = match.groups()

                            # Convert values to float
                            values = list(map(float, filter(None, fuzzy_set_values)))

                            # Validate fuzzy set values within the variable's range
                            if not all(variable.lower <= val <= variable.upper for val in values):
                                print(f"Invalid input. Fuzzy set values must be within the range of variable '{var_name}' [{variable.lower}, {variable.upper}].")
                                continue

                            if fuzzy_set_type == 'TRI' and len(values) == 3:
                                fuzzy_set = FuzzySet(fuzzy_set_name, fuzzy_set_type, values)
                                # Check if the fuzzy set already exists for the variable
                                if any(existing_set.name == fuzzy_set.name for existing_set in variable.fuzzy_sets):
                                    print(f"Fuzzy set '{fuzzy_set.name}' already exists for variable '{var_name}'. Please enter a unique fuzzy set name.")
                                else:
                                    variable.set_fuzzy_set(fuzzy_set)
                            elif fuzzy_set_type == 'TRAP' and len(values) == 4:
                                fuzzy_set = FuzzySet(fuzzy_set_name, fuzzy_set_type, values)
                                # Check if the fuzzy set already exists for the variable
                                if any(existing_set.name == fuzzy_set.name for existing_set in variable.fuzzy_sets):
                                    print(f"Fuzzy set '{fuzzy_set.name}' already exists for variable '{var_name}'. Please enter a unique fuzzy set name.")
                                else:
                                    variable.set_fuzzy_set(fuzzy_set)
                            else:
                                print("Invalid input. Please enter valid values for the fuzzy set type.")
            else:
                print(f"Variable '{var_name}' not exists.")
                system_menu(fuzzy_system)


        elif choice == '3':
            # Enter rules
            print("\nEnter the rule in this format: (Press x to finish)")
            print("IN_variable set operator IN_variable set => OUT_variable set")
            print("-------------------------------------------------------------")

            while True:
                rule_text = input()
                if rule_text == 'x':
                    break

                vars = []
                sets = []
                operators = []

                pattern = re.compile(r'\s*(\w+)\s+(\w+)\s')
                matches = pattern.findall(rule_text)
                if len(matches) < 1:
                    print("Invalid rule format. Please enter the rule in the correct format.")
                else:
                    vars.append(matches[0][0])
                    sets.append(matches[0][1])

                    index = rule_text.find(matches[0][1])
                    index += len(matches[0][1])

                    pattern1 = re.compile(r'\s*(\w+)\s+(\w+)\s+(\w+)\s*')
                    matches1 = pattern1.findall(rule_text[index:])
                    if len(matches1)<1:
                        print("Invalid rule format. Please enter the rule in the correct format.")
                    else:
                        for match in matches1:
                            operators.append(match[0])
                            vars.append(match[1])
                            sets.append(match[2])

                        pattern2 = re.compile(r'\s*=>\s+(\w+)\s+(\w+)\s*')
                        matches2 = pattern2.findall(rule_text)

                        pattern3 = re.compile(r'^(\w+\s+\w+)\s+((and|and_not|or|or_not)\s+(\w+\s+\w+)\s+)+=>\s+(\w+)\s+(\w+)\s*$')

                        result = pattern3.match(rule_text)

                        if len(matches2) != 1 or not result:
                            print("Invalid rule format. Please enter the rule in the correct format.")
                        else:
                            outVar = matches2[0][0]
                            outSet = matches2[0][1]

                            flag = True
                            for i in range(len(vars)):
                                if not checkRule(fuzzy_system,vars[i],sets[i],'IN'):
                                    flag = False
                                    print("Invalid rule. Ensure that variables and sets mentioned in the rule exist.")
                                    break
                            if flag:
                                if not checkRule(fuzzy_system, outVar, outSet,'OUT'):
                                    flag = False
                                    print("Invalid rule. Ensure that variables and sets mentioned in the rule exist.")
                            if flag:
                                rule = Rule(vars, sets, operators, outVar, outSet, rule_text)
                                if checkExistRule(fuzzy_system.rules, rule):
                                    print('Duplicate rule.')
                                else:
                                    fuzzy_system.add_rule(rule)


        elif choice == '4':
            if checkFuzzySystem(fuzzy_system):
                for variable in fuzzy_system.variables:
                    if variable.type == 'IN':
                        crisp = float(input(variable.name + ": "))
                        variable.crisp_value = crisp
                print('Running the simulation…')
                degree_member_ship = fuzzification(fuzzy_system)
                print('Fuzzification => done')
                inferences = Inference(degree_member_ship, fuzzy_system)
                print('Inference => done')
                fuzzy_system = defuzzification(inferences, fuzzy_system)
                print('Defuzzification => done')
                maxi = 0
                fuzzySet = ''
                for variable in fuzzy_system.variables:
                    if variable.type == 'OUT':
                        print(variable.crisp_value)
                        fuzzysets = selectFuzzySets(variable)  # ex (risk=37.5) -> (low, normal)
                        for fuzzyset in fuzzysets:
                            points = linePoints(fuzzyset, variable)  # ex low points = [[25,1], [50,0]]
                            y = degreeMemberShip(variable.crisp_value, points)
                            if y > maxi:
                                maxi = y
                                fuzzySet = fuzzyset.name
                        print('\nThe predicted', variable.name, 'is', fuzzySet,'(' + str(round(variable.crisp_value, 2)) + ')')

        elif choice.lower() == 'close':
            main_menu()

        else:
            print('Invalid Input')


if __name__ == "__main__":
    main_menu()
