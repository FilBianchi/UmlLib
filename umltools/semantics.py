"""Dispatch explicitly translated Python operations and derived properties."""
import xml.etree.ElementTree as ET
from .specification import PROPERTY_RELATIONS, reference
from .collections import UmlCollection
from .native import invoke, DERIVATIONS, NativeNotImplemented, unique


def operation(self, owner, name, args=(), kwargs=None):
    kwargs = kwargs or {}
    spec = next(base.__dict__['__spec__'] for base in type(self).__mro__ if '__spec__' in base.__dict__ and base.__dict__['__spec__'].name == owner)
    node = ET.fromstring(spec.operations[name])
    parameters = [p.get('name') for p in node.findall('ownedParameter') if p.get('direction', 'in') != 'return']
    kwargs = {key[:-1] if key.endswith('_') and key[:-1] in parameters else key: value for key, value in kwargs.items()}
    if len(args) > len(parameters) or set(kwargs) - set(parameters):
        raise TypeError(f'Invalid arguments to {owner}.{name}')
    variables = dict(zip(parameters, args))
    if set(variables) & set(kwargs): raise TypeError('Duplicate operation argument')
    variables.update(kwargs)
    if set(variables) != set(parameters): raise TypeError(f'Expected parameters: {parameters}')
    for parameter in node.findall('ownedParameter'):
        if parameter.get('direction', 'in') == 'return': continue
        parameter_name = parameter.get('name')
        value = variables[parameter_name]
        upper = parameter.find('upperValue')
        high = '1' if upper is None else upper.get('value', '0')
        lower = parameter.find('lowerValue')
        low = 1 if lower is None else int(lower.get('value', '0'))
        many = high == '*' or int(high) > 1
        if many and not isinstance(value, (list, tuple, UmlCollection)): raise TypeError(f'{owner}.{name} requires a collection')
        values = list(value) if many else [] if value is None else [value]
        if len(values) < low or high != '*' and len(values) > int(high): raise ValueError(f'Argument multiplicity violated: {owner}.{name}')
        type_name = reference(parameter, 'type')
        expected = self.__registry__.get(type_name) or {'Boolean': bool, 'String': str, 'Integer': int, 'Real': (int, float), 'UnlimitedNatural': (int, float)}.get(type_name)
        for item in values:
            if expected and not isinstance(item, expected): raise TypeError(f'{owner}.{name} requires {type_name}')
            if type_name in ('Integer', 'Real', 'UnlimitedNatural') and isinstance(item, bool): raise TypeError(f'{owner}.{name} requires a number')
            if type_name == 'UnlimitedNatural' and not (type(item) is int and item >= 0 or type(item) is float and item == float('inf')): raise ValueError('Invalid UnlimitedNatural argument')
    return invoke(self, f'{owner}.{name}', variables)


def derive(self, prop):
    if prop.id in DERIVATIONS: return DERIVATIONS[prop.id](self)
    if prop.id == 'Element-owner': return self._container
    if prop.id == 'Element-ownedElement':
        return unique(child for name, p in self.properties().items() if p.flags.get('aggregation') == 'composite' and p.flags.get('isDerived') != 'true' for child in self._items(getattr(self, name)))
    if prop.id == 'NamedElement-namespace':
        container = self._container
        if container is None: return None
        owned_member = next((p for p in container.properties().values() if p.id == 'Namespace-ownedMember'), None)
        if owned_member and self in derive(container, owned_member): return container
        return None
    if prop.flags.get('isDerivedUnion') == 'true':
        values = []
        def subsets(identifier, target, visited):
            if identifier in visited: return False
            visited = visited | {identifier}
            relations = PROPERTY_RELATIONS.get(identifier, ())
            return target in relations or any(subsets(reference, target, visited) for reference in relations)
        for name, candidate in self.properties().items():
            if candidate.id != prop.id and candidate.flags.get('isDerived') != 'true' and subsets(candidate.id, prop.id, set()):
                for value in self._items(getattr(self, name)):
                    if value not in values: values.append(value)
        return values if prop.upper is None or prop.upper > 1 else (values[0] if values else None)
    for base in type(self).__mro__:
        spec = base.__dict__.get('__spec__')
        if spec and prop.name in spec.operations:
            return operation(self, spec.name, prop.name)
    raise NativeNotImplemented(f'No Python derivation for {prop.id}')
