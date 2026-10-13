from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._StructuredActivityNode import StructuredActivityNode

class ConditionalNode(StructuredActivityNode):
    """UML metaclass ConditionalNode."""
    __spec__ = SPECIFICATIONS['ConditionalNode']
    clause: list[Clause]
    isAssured: bool | None
    isDeterminate: bool | None
    result: list[OutputPin]
