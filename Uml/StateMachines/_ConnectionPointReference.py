from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..StateMachines._Vertex import Vertex

class ConnectionPointReference(Vertex):
    """UML metaclass ConnectionPointReference."""
    __spec__ = SPECIFICATIONS['ConnectionPointReference']
    entry: list[Pseudostate]
    exit: list[Pseudostate]
    state: State | None
    def isConsistentWith(self, *args, **kwargs):
        try:
            return _operation(self, 'ConnectionPointReference', 'isConsistentWith', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
