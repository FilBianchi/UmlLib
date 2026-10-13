from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._DirectedRelationship import DirectedRelationship

class ProfileApplication(DirectedRelationship):
    """UML metaclass ProfileApplication."""
    __spec__ = SPECIFICATIONS['ProfileApplication']
    appliedProfile: Profile | None
    applyingPackage: Package | None
    isStrict: bool | None
