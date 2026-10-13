from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._WriteVariableAction import WriteVariableAction

class AddVariableValueAction(WriteVariableAction):
    """UML metaclass AddVariableValueAction."""
    __spec__ = SPECIFICATIONS['AddVariableValueAction']
    insertAt: InputPin | None
    isReplaceAll: bool | None
