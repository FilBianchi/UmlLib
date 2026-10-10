"""UML 2.5.1 Classification package."""
from importlib import import_module

__all__ = ['Substitution', 'BehavioralFeature', 'Classifier', 'ClassifierTemplateParameter', 'Feature', 'Generalization', 'GeneralizationSet', 'InstanceSpecification', 'InstanceValue', 'Operation', 'OperationTemplateParameter', 'Parameter', 'ParameterSet', 'Property', 'RedefinableElement', 'RedefinableTemplateSignature', 'Slot', 'StructuralFeature', 'AggregationKind', 'CallConcurrencyKind', 'ParameterDirectionKind', 'ParameterEffectKind']

def __getattr__(name):
    if name not in __all__: raise AttributeError(name)
    value = getattr(import_module("._" + name, __name__), name)
    globals()[name] = value
    return value
