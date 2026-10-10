from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._PackageableElement import PackageableElement

class Observation(PackageableElement):
    """UML metaclass Observation."""
    __spec__ = SPECIFICATIONS['Observation']
