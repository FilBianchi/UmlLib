from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._Action import Action

class TestIdentityAction(Action):
    """UML metaclass TestIdentityAction."""
    __spec__ = SPECIFICATIONS['TestIdentityAction']
    first: InputPin | None
    result: OutputPin | None
    second: InputPin | None
