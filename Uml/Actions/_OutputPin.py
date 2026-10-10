from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._Pin import Pin

class OutputPin(Pin):
    """UML metaclass OutputPin."""
    __spec__ = SPECIFICATIONS['OutputPin']
