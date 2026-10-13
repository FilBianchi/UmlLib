"""UML 2.4.1 StructuredClassifiers package."""
from importlib import import_module

__all__ = ['Association', 'AssociationClass', 'Class', 'Collaboration', 'CollaborationUse', 'Component', 'ComponentRealization', 'ConnectableElement', 'ConnectableElementTemplateParameter', 'Connector', 'ConnectorEnd', 'EncapsulatedClassifier', 'Port', 'StructuredClassifier', 'ConnectorKind']

def __getattr__(name):
    if name not in __all__: raise AttributeError(name)
    value = getattr(import_module("._" + name, __name__), name)
    globals()[name] = value
    return value
