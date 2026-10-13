from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._VariableAction import VariableAction

class WriteVariableAction(VariableAction):
    """UML metaclass WriteVariableAction."""
    __spec__ = SPECIFICATIONS['WriteVariableAction']
    value: InputPin | None
