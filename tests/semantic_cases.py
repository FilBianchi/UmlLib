"""Link independent behavioral examples to specification rules."""
def verifies(*identifiers):
    def decorate(function):
        function.semantic_rules = identifiers
        return function
    return decorate
