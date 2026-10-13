from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Activities._ControlNode import ControlNode

class MergeNode(ControlNode):
    """UML metaclass MergeNode."""
    __spec__ = SPECIFICATIONS['MergeNode']
