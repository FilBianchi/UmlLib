from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._StructuredActivityNode import StructuredActivityNode

class SequenceNode(StructuredActivityNode):
    """UML metaclass SequenceNode."""
    __spec__ = SPECIFICATIONS['SequenceNode']
    executableNode: list[ExecutableNode]
