from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Interactions._InteractionFragment import InteractionFragment

class Continuation(InteractionFragment):
    """UML metaclass Continuation."""
    __spec__ = SPECIFICATIONS['Continuation']
    setting: bool | None
