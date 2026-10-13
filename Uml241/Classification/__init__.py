"""UML 2.4.1 Classification package."""
from importlib import import_module

__all__ = ['BehavioralFeature', 'Classifier', 'ClassifierTemplateParameter', 'Feature', 'Generalization', 'GeneralizationSet', 'InstanceSpecification', 'InstanceValue', 'Operation', 'OperationTemplateParameter', 'Parameter', 'ParameterSet', 'Property', 'RedefinableElement', 'RedefinableTemplateSignature', 'Slot', 'StructuralFeature', 'Substitution', 'AggregationKind', 'CallConcurrencyKind', 'ParameterDirectionKind', 'ParameterEffectKind']

def __getattr__(name):
    if name not in __all__: raise AttributeError(name)
    value = getattr(import_module("._" + name, __name__), name)
    globals()[name] = value
    return value
