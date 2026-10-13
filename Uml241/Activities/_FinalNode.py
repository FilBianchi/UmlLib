from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Activities._ControlNode import ControlNode

class FinalNode(ControlNode):
    """UML metaclass FinalNode."""
    __spec__ = SPECIFICATIONS['FinalNode']
