from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._Action import Action

class ReadLinkObjectEndQualifierAction(Action):
    """UML metaclass ReadLinkObjectEndQualifierAction."""
    __spec__ = SPECIFICATIONS['ReadLinkObjectEndQualifierAction']
    object: InputPin | None
    qualifier: Property | None
    result: OutputPin | None
