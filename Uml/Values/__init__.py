"""UML 2.5.1 Values package."""
from importlib import import_module

__all__ = ['Duration', 'DurationConstraint', 'DurationInterval', 'DurationObservation', 'Expression', 'Interval', 'IntervalConstraint', 'LiteralBoolean', 'LiteralInteger', 'LiteralNull', 'LiteralReal', 'LiteralSpecification', 'LiteralString', 'LiteralUnlimitedNatural', 'Observation', 'OpaqueExpression', 'StringExpression', 'TimeConstraint', 'TimeExpression', 'TimeInterval', 'TimeObservation', 'ValueSpecification']

def __getattr__(name):
    if name not in __all__: raise AttributeError(name)
    value = getattr(import_module("._" + name, __name__), name)
    globals()[name] = value
    return value
