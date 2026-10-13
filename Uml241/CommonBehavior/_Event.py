from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._PackageableElement import PackageableElement

class Event(PackageableElement):
    """UML metaclass Event."""
    __spec__ = SPECIFICATIONS['Event']
