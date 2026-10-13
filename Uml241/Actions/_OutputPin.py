from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._Pin import Pin

class OutputPin(Pin):
    """UML metaclass OutputPin."""
    __spec__ = SPECIFICATIONS['OutputPin']
