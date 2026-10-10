"""UML 2.5.1 CommonStructure package."""
from importlib import import_module

__all__ = ['Abstraction', 'Comment', 'Constraint', 'Dependency', 'DirectedRelationship', 'Element', 'ElementImport', 'MultiplicityElement', 'NamedElement', 'Namespace', 'PackageableElement', 'PackageImport', 'ParameterableElement', 'Realization', 'Relationship', 'TemplateableElement', 'TemplateBinding', 'TemplateParameter', 'TemplateParameterSubstitution', 'TemplateSignature', 'Type', 'TypedElement', 'Usage', 'VisibilityKind']

def __getattr__(name):
    if name not in __all__: raise AttributeError(name)
    value = getattr(import_module("._" + name, __name__), name)
    globals()[name] = value
    return value
