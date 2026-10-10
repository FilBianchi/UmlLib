from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._PackageableElement import PackageableElement

class Event(PackageableElement):
    """UML metaclass Event."""
    __spec__ = SPECIFICATIONS['Event']
