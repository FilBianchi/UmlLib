from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._DirectedRelationship import DirectedRelationship
from ..CommonStructure._NamedElement import NamedElement

class Include(DirectedRelationship, NamedElement):
    """UML metaclass Include."""
    __spec__ = SPECIFICATIONS['Include']
    addition: UseCase | None
    includingCase: UseCase | None
