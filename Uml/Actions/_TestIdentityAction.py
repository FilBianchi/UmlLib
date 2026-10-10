from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._Action import Action

class TestIdentityAction(Action):
    """UML metaclass TestIdentityAction."""
    __spec__ = SPECIFICATIONS['TestIdentityAction']
    first: InputPin | None
    result: OutputPin | None
    second: InputPin | None
