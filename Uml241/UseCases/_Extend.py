from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._NamedElement import NamedElement
from ..CommonStructure._DirectedRelationship import DirectedRelationship

class Extend(NamedElement, DirectedRelationship):
    """UML metaclass Extend."""
    __spec__ = SPECIFICATIONS['Extend']
    condition: Constraint | None
    extendedCase: UseCase | None
    extension: UseCase | None
    extensionLocation: list[ExtensionPoint]
