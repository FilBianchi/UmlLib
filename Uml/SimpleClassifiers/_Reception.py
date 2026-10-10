from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Classification._BehavioralFeature import BehavioralFeature

class Reception(BehavioralFeature):
    """UML metaclass Reception."""
    __spec__ = SPECIFICATIONS['Reception']
    signal: Signal | None
