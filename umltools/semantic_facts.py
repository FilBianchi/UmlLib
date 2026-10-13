"""Explicit trusted facts for obligations absent from the UML metamodel syntax."""
from weakref import WeakKeyDictionary
from .native import require_version,NativeNotImplemented
from .evaluation_context import profile_evaluation

_facts=WeakKeyDictionary()
BOOLEAN_FACTS=frozenset(('autonomous','starting_time_available','trigger_parameters_assigned','pure'))


def register_semantic_facts(element,**facts):
    require_version(element);element._ensure_alive()
    if profile_evaluation.get():raise ValueError('Cannot change semantic facts during evaluation')
    if set(facts)-BOOLEAN_FACTS:raise ValueError('Unknown semantic fact')
    if any(type(v) is not bool for v in facts.values()):raise TypeError('Semantic facts must be exact Boolean values')
    _facts.setdefault(element,{}).update(facts)


def semantic_fact(element,name):
    require_version(element);element._ensure_alive()
    if name not in _facts.get(element,{}):raise NativeNotImplemented('Missing trusted semantic fact: '+name)
    return _facts[element][name]
