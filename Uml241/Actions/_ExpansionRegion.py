from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._StructuredActivityNode import StructuredActivityNode

class ExpansionRegion(StructuredActivityNode):
    """UML metaclass ExpansionRegion."""
    __spec__ = SPECIFICATIONS['ExpansionRegion']
    inputElement: list[ExpansionNode]
    mode: ExpansionKind | None
    outputElement: list[ExpansionNode]
