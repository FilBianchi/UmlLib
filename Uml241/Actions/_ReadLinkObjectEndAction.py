from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._Action import Action

class ReadLinkObjectEndAction(Action):
    """UML metaclass ReadLinkObjectEndAction."""
    __spec__ = SPECIFICATIONS['ReadLinkObjectEndAction']
    end: Property | None
    object: InputPin | None
    result: OutputPin | None
