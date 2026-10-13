from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._Action import Action

class AcceptEventAction(Action):
    """UML metaclass AcceptEventAction."""
    __spec__ = SPECIFICATIONS['AcceptEventAction']
    isUnmarshall: bool | None
    result: list[OutputPin]
    trigger: list[Trigger]
