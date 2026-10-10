"""Language adapters may declare facts about opaque expressions without running OCL.

These are facts supplied by a trusted language analyser, not guesses from strings.
Missing facts remain unsupported validation obligations.
"""
from dataclasses import dataclass
from weakref import WeakKeyDictionary, WeakSet
from .native import kind, NativeNotImplemented


@dataclass(frozen=True)
class ExpressionFacts:
    references: tuple | None = None
    constant: bool | None = None
    pure: bool | None = None


_facts = WeakKeyDictionary()
_collection_types = WeakSet()


def register_collection_type(classifier):
    """Declare a domain type whose individual instances are collections."""
    if not kind(classifier, classifier, 'Classifier'): raise TypeError('Expected a UML Classifier')
    _collection_types.add(classifier)


def is_collection_type(classifier): return classifier in _collection_types


def register_expression_facts(expression, *, references=None, constant=None, pure=None):
    if not kind(expression, expression, 'ValueSpecification'): raise TypeError('Expected a UML ValueSpecification')
    if constant is not None and type(constant) is not bool: raise TypeError('constant must be Boolean')
    if pure is not None and type(pure) is not bool: raise TypeError('pure must be Boolean')
    _facts[expression] = ExpressionFacts(None if references is None else tuple(references), constant, pure)


def expression_fact(expression, name):
    if expression is None: raise ValueError('Missing expression')
    explicit = _facts.get(expression)
    if explicit is not None and getattr(explicit, name) is not None: return getattr(explicit, name)
    if kind(expression, expression, 'LiteralSpecification'):
        return () if name == 'references' else True
    if kind(expression, expression, 'InstanceValue'):
        return (expression.instance,) if name == 'references' else name == 'pure'
    if kind(expression, expression, 'StringExpression'):
        parts = expression.subExpression or expression.operand
        values = [expression_fact(part, name) for part in parts]
        return tuple(r for v in values for r in v) if name == 'references' else all(values)
    raise NativeNotImplemented(f'{name} of {type(expression).__name__} requires a language analyser')
