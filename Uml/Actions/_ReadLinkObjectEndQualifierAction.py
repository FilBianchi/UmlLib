from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._Action import Action

class ReadLinkObjectEndQualifierAction(Action):
    """UML metaclass ReadLinkObjectEndQualifierAction."""
    __spec__ = SPECIFICATIONS['ReadLinkObjectEndQualifierAction']
    object: InputPin | None
    qualifier: Property | None
    result: OutputPin | None
