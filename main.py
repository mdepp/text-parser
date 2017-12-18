import regex
from dependencies import Dependency, get_unresolvable_dependencies

def remove_comments(line):
    """
    Return a new line string without comments. This is not actually guaranteed
    to be a different string object that the old line string.
    """
    comment_expr = regex.compile('#')
    match = comment_expr.match(line)
    if match:
        return line[:match.start()]
    else:
        return line

def get_variable_pattern(line):
    """
    Isolate the variable and pattern from the line string (of the form
    $VARIABLE = pattern), and return them separately.
    """
    expr = regex.compile('^\\s*\\$(?P<variable>[a-zA-Z]+)\\s*=\\s*(?P<pattern>.*)')
    match = expr.match(line)
    if match:
        return match.group('variable'), match.group('pattern')
    else:
        return None, None


def substitute_variables(patterns):
    """
    When given a dictionary of variables to patterns, with variables inside
    patterns given by $VARIABLE, this substitutes expressions for variables
    as necessary (while avoiding circular dependencies)
    """
    
    match_variables = regex.compile("\\$([a-zA-Z]+)")

    # Check if dependencies can be resolved
    dependencies = {}
    for variable, pattern in patterns.items():
        if not variable in dependencies:
            dependencies[variable] = Dependency()
        dependencies[variable].dependsOn = regex.findall(match_variables, pattern)[:]
    
    unresolvable_dependencies = get_unresolvable_dependencies(dependencies)
    if unresolvable_dependencies:
        print('Cannot resolve variable dependencies: ', end='')
        print(', '.join(name for name,object in unresolvable_dependencies.items()))
        return
    
    # Now that all dependencies are resolvable, we can use this simple algorithm
    # which is guaranteed to stop after a finite number of steps.
    changed = True
    while changed: # Loop until patterns have stabilized
        changed = False
        for variable, pattern in patterns.items():
            # Replace a variable name in pattern using other variable patterns
            match = match_variables.search(pattern)
            if match:
                # Replace pattern with a new pattern with variable name replaced with pattern
                if match.group(1) not in patterns:
                    print('Invalid variable "' + match.group(1) + '", even though dependencies should be resolvable.')
                
                patterns[variable] = pattern[:match.start()] + patterns[match.group(1)] + pattern[match.end():]
                changed = True
    
    return patterns

def load_patterns():
    """
    Reads 'patterns.txt' for command regex patterns, substitutes variables as
    appropriate, and returns a dictionary of variables to patterns.
    """
    patterns = {} # Variables to patterns

    # Read patterns from file
    with open('patterns.txt') as f:
        for line in f:
            # Preprocessing
            # should process whitespace here
            # Ignore all comments (for now don't even ignore comments in strings)
            
            line = remove_comments(line) # Remove comments
            line = line.strip() # Remove whitespace
            if not line: # Skip blank lines
                continue

            variable, pattern = get_variable_pattern(line)
            #print('Variable', variable)
            #print('Pattern:', pattern)
            if variable:
                patterns[variable] = pattern

    # Make variable substitutions
    patterns = substitute_variables(patterns)
    if not patterns:
        print("Could not substitute variables.")
        return

    return patterns

def load_action_list():
    """
    Reads 'action-list.txt' for all valid action IDs and returns them as a list.
    """
    actions = []
    with open('action-list.txt') as f:
        for line in f:
            # Remove comments and initial/trailing whitespace
            line = remove_comments(line)
            line = line.strip()
            if not line:
                continue # Skip blank lines

            actions.append(line)

    return actions

def main():
    """
    Main program function
    """
    # Load command patterns
    patterns = load_patterns()
    
    if not patterns:
        print('Could not read patterns.')
        return
    
    # Display all patterns
    for name, pattern in patterns.items():
        print(name, ':', pattern)

    # Load action list
    actions = load_action_list()


    reg = regex.compile('^\\s*' + patterns['COMMANDS'] + '\\s*$')
    command = input('>')
    if reg.search(command):
        print("Valid command")
    else:
        print("Invalid command")

    for action in actions:
        try:
            results = [m.captures(action) for m in reg.finditer(command)]
        except IndexError:
            results = None
        if not results:
            continue
        for result in results[0]:
            if not result:
                continue
            print('Action({name}): {text}'.format(name=action, text=result))
            try:
                print('Subjects:', [m.captures('subject')[0] for m in reg.finditer(result)])
            except:
                pass
            try:
                print('Objects:', [m.captures('object')[0] for m in reg.finditer(result)])
            except:
                pass


main()