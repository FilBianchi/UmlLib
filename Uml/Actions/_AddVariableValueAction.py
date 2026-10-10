from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._WriteVariableAction import WriteVariableAction

class AddVariableValueAction(WriteVariableAction):
    """UML metaclass AddVariableValueAction."""
    __spec__ = SPECIFICATIONS['AddVariableValueAction']
    insertAt: InputPin | None
    isReplaceAll: bool | None
