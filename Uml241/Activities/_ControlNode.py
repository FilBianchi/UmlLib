from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Activities._ActivityNode import ActivityNode

class ControlNode(ActivityNode):
    """UML metaclass ControlNode."""
    __spec__ = SPECIFICATIONS['ControlNode']
