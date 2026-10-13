from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._Relationship import Relationship

class DirectedRelationship(Relationship):
    """UML metaclass DirectedRelationship."""
    __spec__ = SPECIFICATIONS['DirectedRelationship']
    source: list[Element]
    target: list[Element]
