from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._Action import Action

class AcceptEventAction(Action):
    """UML metaclass AcceptEventAction."""
    __spec__ = SPECIFICATIONS['AcceptEventAction']
    isUnmarshall: bool | None
    result: list[OutputPin]
    trigger: list[Trigger]
