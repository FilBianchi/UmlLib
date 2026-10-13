from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._Action import Action

class StartClassifierBehaviorAction(Action):
    """UML metaclass StartClassifierBehaviorAction."""
    __spec__ = SPECIFICATIONS['StartClassifierBehaviorAction']
    object: InputPin | None
