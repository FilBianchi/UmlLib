from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._NamedElement import NamedElement

class CollaborationUse(NamedElement):
    """UML metaclass CollaborationUse."""
    __spec__ = SPECIFICATIONS['CollaborationUse']
    roleBinding: list[Dependency]
    type: Collaboration | None
