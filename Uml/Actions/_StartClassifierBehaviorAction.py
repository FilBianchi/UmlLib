from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._Action import Action

class StartClassifierBehaviorAction(Action):
    """UML metaclass StartClassifierBehaviorAction."""
    __spec__ = SPECIFICATIONS['StartClassifierBehaviorAction']
    object: InputPin | None
