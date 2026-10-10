from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..StateMachines._Vertex import Vertex

class Pseudostate(Vertex):
    """UML metaclass Pseudostate."""
    __spec__ = SPECIFICATIONS['Pseudostate']
    kind: PseudostateKind | None
    state: State | None
    stateMachine: StateMachine | None
    def isConsistentWith(self, *args, **kwargs):
        try:
            return _operation(self, 'Pseudostate', 'isConsistentWith', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
