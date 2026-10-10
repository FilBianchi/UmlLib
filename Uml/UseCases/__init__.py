"""UML 2.5.1 UseCases package."""
from importlib import import_module

__all__ = ['Actor', 'Extend', 'ExtensionPoint', 'Include', 'UseCase']

def __getattr__(name):
    if name not in __all__: raise AttributeError(name)
    value = getattr(import_module("._" + name, __name__), name)
    globals()[name] = value
    return value
