from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Activities._FinalNode import FinalNode

class ActivityFinalNode(FinalNode):
    """UML metaclass ActivityFinalNode."""
    __spec__ = SPECIFICATIONS['ActivityFinalNode']
