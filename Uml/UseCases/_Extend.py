from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._NamedElement import NamedElement
from ..CommonStructure._DirectedRelationship import DirectedRelationship

class Extend(NamedElement, DirectedRelationship):
    """UML metaclass Extend."""
    __spec__ = SPECIFICATIONS['Extend']
    condition: Constraint | None
    extendedCase: UseCase | None
    extension: UseCase | None
    extensionLocation: list[ExtensionPoint]
