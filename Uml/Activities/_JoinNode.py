from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Activities._ControlNode import ControlNode

class JoinNode(ControlNode):
    """UML metaclass JoinNode."""
    __spec__ = SPECIFICATIONS['JoinNode']
    isCombineDuplicate: bool | None
    joinSpec: ValueSpecification | None
