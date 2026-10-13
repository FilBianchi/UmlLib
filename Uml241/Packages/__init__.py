"""UML 2.4.1 Packages package."""
from importlib import import_module

__all__ = ['Extension', 'ExtensionEnd', 'Image', 'Model', 'Package', 'PackageMerge', 'Profile', 'ProfileApplication', 'Stereotype']

def __getattr__(name):
    if name not in __all__: raise AttributeError(name)
    value = getattr(import_module("._" + name, __name__), name)
    globals()[name] = value
    return value
