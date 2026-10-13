"""UML 2.4.1 CommonBehavior package."""
from importlib import import_module

__all__ = ['AnyReceiveEvent', 'Behavior', 'CallEvent', 'ChangeEvent', 'Event', 'FunctionBehavior', 'MessageEvent', 'OpaqueBehavior', 'SignalEvent', 'TimeEvent', 'Trigger']

def __getattr__(name):
    if name not in __all__: raise AttributeError(name)
    value = getattr(import_module("._" + name, __name__), name)
    globals()[name] = value
    return value
