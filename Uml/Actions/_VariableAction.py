from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._Action import Action

class VariableAction(Action):
    """UML metaclass VariableAction."""
    __spec__ = SPECIFICATIONS['VariableAction']
    variable: Variable | None
