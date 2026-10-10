from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._VariableAction import VariableAction

class ReadVariableAction(VariableAction):
    """UML metaclass ReadVariableAction."""
    __spec__ = SPECIFICATIONS['ReadVariableAction']
    result: OutputPin | None
