from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._Action import Action

class VariableAction(Action):
    """UML metaclass VariableAction."""
    __spec__ = SPECIFICATIONS['VariableAction']
    variable: Variable | None
