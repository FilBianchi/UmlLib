from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._PackageableElement import PackageableElement

class Observation(PackageableElement):
    """UML metaclass Observation."""
    __spec__ = SPECIFICATIONS['Observation']
