from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._DirectedRelationship import DirectedRelationship
from ..CommonStructure._NamedElement import NamedElement

class Include(DirectedRelationship, NamedElement):
    """UML metaclass Include."""
    __spec__ = SPECIFICATIONS['Include']
    addition: UseCase | None
    includingCase: UseCase | None
