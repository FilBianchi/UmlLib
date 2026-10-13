from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Interactions._ExecutionSpecification import ExecutionSpecification

class ActionExecutionSpecification(ExecutionSpecification):
    """UML metaclass ActionExecutionSpecification."""
    __spec__ = SPECIFICATIONS['ActionExecutionSpecification']
    action: Action | None
