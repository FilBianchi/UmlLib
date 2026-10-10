from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonBehavior._Behavior import Behavior

class OpaqueBehavior(Behavior):
    """UML metaclass OpaqueBehavior."""
    __spec__ = SPECIFICATIONS['OpaqueBehavior']
    body: list[str]
    language: list[str]
