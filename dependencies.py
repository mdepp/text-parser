class Dependency:
    def __init__(self):
        """
        Initialize the dependency object with a name (which is used as a 
        convenience to identify these objects, but not actually used anywhere
        in the check_dependencies algorithm)
        """
        self.dependsOn = [] # Expected to contain Dependency objects.

def get_unresolvable_dependencies(dependency_map):
    """
    When given a dictionary of names to Dependency objects, this function will find all
    unmet, circular, and otherwise unresolvable dependencies.
    """
    changed = True

    while changed:
        changed = False
        for name, object in dependency_map.items():
            if object.dependsOn: # this object has dependencies
                # Attempt to reduce dependencies by one step
                if all(not(dependency_map[dep].dependsOn) for dep in object.dependsOn):
                    # None of this object's dependencies have any dependencies,
                    # so dependency can be reduced this step
                    object.dependsOn = None
                    changed = True
    
    # Dependency list has stabilized. Any remaining dependencies cannot be
    # resolved. Compile a list of these dependencies
    unresolvable_dependencies = {name : object for name,object in dependency_map.items() if object.dependsOn}
    return unresolvable_dependencies