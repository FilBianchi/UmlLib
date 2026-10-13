from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Classification._BehavioralFeature import BehavioralFeature

class Reception(BehavioralFeature):
    """UML metaclass Reception."""
    __spec__ = SPECIFICATIONS['Reception']
    signal: Signal | None
