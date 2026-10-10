from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._Pin import Pin

class InputPin(Pin):
    """UML metaclass InputPin."""
    __spec__ = SPECIFICATIONS['InputPin']
