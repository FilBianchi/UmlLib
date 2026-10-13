from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..StateMachines._Vertex import Vertex

class ConnectionPointReference(Vertex):
    """UML metaclass ConnectionPointReference."""
    __spec__ = SPECIFICATIONS['ConnectionPointReference']
    entry: list[Pseudostate]
    exit: list[Pseudostate]
    state: State | None
