from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._WriteVariableAction import WriteVariableAction

class RemoveVariableValueAction(WriteVariableAction):
    """UML metaclass RemoveVariableValueAction."""
    __spec__ = SPECIFICATIONS['RemoveVariableValueAction']
    isRemoveDuplicates: bool | None
    removeAt: InputPin | None
