"""Operation parameter contracts, checked without evaluating specification OCL."""
from math import isfinite
from .collections import UmlCollection
from .specification import reference


class OperationResultError(ValueError):
    """A native query returned a value outside its effective UML signature."""
    def __init__(self, operation, reason):
        self.operation, self.reason = operation, reason
        super().__init__(f'Invalid result from {operation}: {reason}')


# These source inconsistencies are explicit, not blanket exceptions for null results.
SIGNATURE_INTERPRETATIONS = {
    'NamedElement.qualifiedName': 'The derived property is optional and the body returns null for unnamed elements.',
    'LiteralString.stringValue': 'LiteralString.value is optional; its direct-value query may return null.',
    'ElementImport.getName': 'Alias and the imported element name can both be absent; the body then returns null.',
    'Namespace.getNamesOfMember': 'The body creates Set{element.name}, which can contain an undefined name.',
}


def multiplicity(node):
    lower, upper = node.find('lowerValue'), node.find('upperValue')
    low = 1 if lower is None else int(lower.get('value', '0'))
    high = '1' if upper is None else upper.get('value', '0')
    return low, None if high == '*' else int(high)


def validate_item(self, value, type_name):
    primitives = {'Boolean': bool, 'String': str, 'Integer': int,
                  'Real': (int, float), 'UnlimitedNatural': (int, float)}
    expected = self.__registry__.get(type_name) or primitives.get(type_name)
    if expected is None:
        if type_name is not None: raise TypeError(f'Unknown UML parameter type: {type_name}')
        return
    if not isinstance(value, expected): raise TypeError(f'Expected {type_name}')
    if type_name in ('Integer', 'Real', 'UnlimitedNatural') and isinstance(value, bool):
        raise TypeError(f'Expected {type_name}, not Boolean')
    if type_name == 'UnlimitedNatural' and not (type(value) is int and value >= 0 or type(value) is float and value == float('inf')):
        raise ValueError('Expected a nonnegative integer or unlimited natural *')
    if type_name == 'Real' and isinstance(value, float) and not isfinite(value):
        raise ValueError('Expected a finite Real value')


def validate_parameter(self, parameter, value, *, operation_id, result=False):
    low, high = multiplicity(parameter)
    if result and operation_id in ('NamedElement.qualifiedName', 'LiteralString.stringValue', 'ElementImport.getName'): low = 0
    many = high is None or high > 1
    ordered = parameter.get('isOrdered', 'false') == 'true'
    collections = (list, tuple, UmlCollection) if ordered else (list, tuple, UmlCollection, set, frozenset)
    if many:
        if not isinstance(value, collections): raise TypeError('Expected an ordered collection' if ordered else 'Expected a collection')
        values = list(value)
    else:
        values = [] if value is None else [value]
    if len(values) < low or high is not None and len(values) > high:
        raise ValueError(f'Multiplicity {low}..{"*" if high is None else high} violated')
    type_name = reference(parameter, 'type')
    for item in values:
        if item is None:
            if result and operation_id == 'Namespace.getNamesOfMember': continue
            raise TypeError('Null collection elements are not allowed')
        validate_item(self, item, type_name)
    if many and parameter.get('isUnique', 'true') == 'true':
        for index, item in enumerate(values):
            if item in values[:index]: raise ValueError('A unique parameter contains duplicate values')


def validate_result(self, node, value, operation_id):
    returns = [p for p in node.findall('ownedParameter') if p.get('direction', 'in') == 'return']
    try:
        if not returns:
            if value is not None: raise ValueError('A void operation returned a value')
        elif len(returns) == 1:
            validate_parameter(self, returns[0], value, operation_id=operation_id, result=True)
        else: raise ValueError('Multiple return parameters require a declared result mapping')
    except (TypeError, ValueError) as error:
        raise OperationResultError(operation_id, str(error)) from error
    return value
