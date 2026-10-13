from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonBehavior._Behavior import Behavior

class OpaqueBehavior(Behavior):
    """UML metaclass OpaqueBehavior."""
    __spec__ = SPECIFICATIONS['OpaqueBehavior']
    body: list[str]
    language: list[str]
