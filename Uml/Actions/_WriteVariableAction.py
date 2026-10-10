from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._VariableAction import VariableAction

class WriteVariableAction(VariableAction):
    """UML metaclass WriteVariableAction."""
    __spec__ = SPECIFICATIONS['WriteVariableAction']
    value: InputPin | None
