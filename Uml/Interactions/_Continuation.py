from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Interactions._InteractionFragment import InteractionFragment

class Continuation(InteractionFragment):
    """UML metaclass Continuation."""
    __spec__ = SPECIFICATIONS['Continuation']
    setting: bool | None
