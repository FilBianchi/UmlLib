from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Activities._ObjectNode import ObjectNode
from ..CommonStructure._MultiplicityElement import MultiplicityElement

class Pin(ObjectNode, MultiplicityElement):
    """UML metaclass Pin."""
    __spec__ = SPECIFICATIONS['Pin']
    isControl: bool | None
    @property
    def upperBound(self):
        return UmlElement.__getattr__(self, 'upperBound')
