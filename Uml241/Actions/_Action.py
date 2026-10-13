from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Activities._ExecutableNode import ExecutableNode

class Action(ExecutableNode):
    """UML metaclass Action."""
    __spec__ = SPECIFICATIONS['Action']
    context: Classifier | None
    input: list[InputPin]
    isLocallyReentrant: bool | None
    localPostcondition: list[Constraint]
    localPrecondition: list[Constraint]
    output: list[OutputPin]
