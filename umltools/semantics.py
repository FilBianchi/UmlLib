"""Dispatch explicitly translated Python operations and derived properties."""
import xml.etree.ElementTree as ET
from contextvars import ContextVar
from .specification import PROPERTY_RELATIONS
from .native import invoke, DERIVATIONS, NativeNotImplemented, unique
from .contracts import validate_parameter, validate_result

# Import-only memoization after the core graph is linked. Normal mutable model
# queries are never cached. The XMI reader suspends/clears this on late resource loads.
_exchange_query_cache = ContextVar('uml_exchange_query_cache', default=None)


def _cached_query(key, function):
    cache = _exchange_query_cache.get()
    try: hash(key)
    except TypeError: cache = None
    if cache is not None and key in cache:
        result = cache[key]
        return list(result) if isinstance(result, list) else result
    result = function()
    if cache is not None: cache[key] = list(result) if isinstance(result, list) else result
    return result


def operation(self, owner, name, args=(), kwargs=None):
    self._ensure_alive()
    return _cached_query(('operation', self, owner, name, tuple(args), tuple(sorted((kwargs or {}).items()))),
                         lambda: _operation(self, owner, name, args, kwargs))


def _operation(self, owner, name, args=(), kwargs=None):
    self._ensure_alive()
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
        validate_parameter(self, parameter, value, operation_id=f'{owner}.{name}')
    result = invoke(self, f'{owner}.{name}', variables)
    return validate_result(self, node, result, f'{owner}.{name}')


def derive(self, prop):
    self._ensure_alive()
    return _cached_query(('derive', self, prop.id), lambda: _derive(self, prop))


def _derive(self, prop):
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
