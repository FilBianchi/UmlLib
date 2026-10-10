from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._StructuredActivityNode import StructuredActivityNode

class ExpansionRegion(StructuredActivityNode):
    """UML metaclass ExpansionRegion."""
    __spec__ = SPECIFICATIONS['ExpansionRegion']
    inputElement: list[ExpansionNode]
    mode: ExpansionKind | None
    outputElement: list[ExpansionNode]
