from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._DirectedRelationship import DirectedRelationship

class ProfileApplication(DirectedRelationship):
    """UML metaclass ProfileApplication."""
    __spec__ = SPECIFICATIONS['ProfileApplication']
    appliedProfile: Profile | None
    applyingPackage: Package | None
    isStrict: bool | None
