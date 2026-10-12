"""Hand-written Python semantics, traced to UML specification identifiers.

The OCL text is reference material, never executed by this runtime.
"""
from contextvars import ContextVar


class NativeNotImplemented(NotImplementedError):
    pass


OPERATIONS = {}
CONSTRAINTS = {}
DERIVATIONS = {}
_queries = ContextVar('uml_native_queries', default=frozenset())


def register(table, *identifiers):
    def decorator(function):
        for identifier in identifiers:
            if identifier in table: raise RuntimeError(f'Duplicate semantic implementation: {identifier}')
            table[identifier] = function
        return function
    return decorator


def query(*identifiers): return register(OPERATIONS, *identifiers)
def invariant(*identifiers): return register(CONSTRAINTS, *identifiers)
def derived(*identifiers): return register(DERIVATIONS, *identifiers)


def invoke(self, identifier, variables):
    self._ensure_alive()
    function = OPERATIONS.get(identifier)
    if function is None: raise NativeNotImplemented(f'Python operation not implemented: {identifier}')
    key = (id(self), identifier)
    active = _queries.get()
    if key in active: raise ValueError(f'Cyclic semantic query: {identifier}')
    token = _queries.set(active | {key})
    try: return function(self, **variables)
    finally: _queries.reset(token)


def check(self, identifier):
    self._ensure_alive()
    function = CONSTRAINTS.get(identifier)
    if function is None: raise NativeNotImplemented(f'Python invariant not implemented: {identifier}')
    result = function(self)
    if type(result) is not bool: raise ValueError(f'Invariant did not return Boolean: {identifier}')
    return result


def unique(values): return list(dict.fromkeys(values))
def kind(self, value, name): return isinstance(value, self.__registry__[name])
def instances(self, name):
    self._ensure_alive()
    extent = self.__instances__ if self._extent is None else self._extent.elements
    return [value for value in extent if not value.is_deleted and value._extent is self._extent and value.__registry__ is self.__registry__ and kind(self, value, name)]


def reverse(self, name, field):
    """Navigate an association-owned end without inventing a UML property."""
    return [value for value in instances(self, name) if self in self._items(getattr(value, field))]


def single(values):
    values = list(values)
    if len(values) > 1: raise ValueError('Association multiplicity exceeded')
    return values[0] if values else None


from . import common_structure, values, classification, state_machines, common_behavior
from . import activities_actions, additional_queries, structured_classifiers, interactions
from . import constraints_basic
from . import constraints_actions
from . import constraints_activities
from . import constraints_interactions
from . import constraints_remaining
from . import information_flows
from . import part_decomposition
