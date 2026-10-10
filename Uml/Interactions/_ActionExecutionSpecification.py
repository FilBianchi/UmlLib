from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Interactions._ExecutionSpecification import ExecutionSpecification

class ActionExecutionSpecification(ExecutionSpecification):
    """UML metaclass ActionExecutionSpecification."""
    __spec__ = SPECIFICATIONS['ActionExecutionSpecification']
    action: Action | None
