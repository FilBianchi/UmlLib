from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._NamedElement import NamedElement

class Vertex(NamedElement):
    """UML metaclass Vertex."""
    __spec__ = SPECIFICATIONS['Vertex']
    container: Region | None
    incoming: list[Transition]
    outgoing: list[Transition]
    def containingStateMachine(self, *args, **kwargs):
        try:
            return _operation(self, 'Vertex', 'containingStateMachine', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
