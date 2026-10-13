from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..StateMachines._Vertex import Vertex

class Pseudostate(Vertex):
    """UML metaclass Pseudostate."""
    __spec__ = SPECIFICATIONS['Pseudostate']
    kind: PseudostateKind | None
    state: State | None
    stateMachine: StateMachine | None
