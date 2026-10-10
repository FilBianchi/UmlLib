from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._Relationship import Relationship

class DirectedRelationship(Relationship):
    """UML metaclass DirectedRelationship."""
    __spec__ = SPECIFICATIONS['DirectedRelationship']
    source: list[Element]
    target: list[Element]
