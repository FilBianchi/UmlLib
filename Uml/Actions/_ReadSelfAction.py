from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._Action import Action

class ReadSelfAction(Action):
    """UML metaclass ReadSelfAction."""
    __spec__ = SPECIFICATIONS['ReadSelfAction']
    result: OutputPin | None
