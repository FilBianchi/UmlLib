from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._WriteVariableAction import WriteVariableAction

class RemoveVariableValueAction(WriteVariableAction):
    """UML metaclass RemoveVariableValueAction."""
    __spec__ = SPECIFICATIONS['RemoveVariableValueAction']
    isRemoveDuplicates: bool | None
    removeAt: InputPin | None
