"""UML 2.4.1 Interactions package."""
from importlib import import_module

__all__ = ['ActionExecutionSpecification', 'BehaviorExecutionSpecification', 'CombinedFragment', 'ConsiderIgnoreFragment', 'Continuation', 'DestructionOccurrenceSpecification', 'ExecutionOccurrenceSpecification', 'ExecutionSpecification', 'Gate', 'GeneralOrdering', 'Interaction', 'InteractionConstraint', 'InteractionFragment', 'InteractionOperand', 'InteractionUse', 'Lifeline', 'Message', 'MessageEnd', 'MessageOccurrenceSpecification', 'OccurrenceSpecification', 'PartDecomposition', 'StateInvariant', 'InteractionOperatorKind', 'MessageKind', 'MessageSort']

def __getattr__(name):
    if name not in __all__: raise AttributeError(name)
    value = getattr(import_module("._" + name, __name__), name)
    globals()[name] = value
    return value
