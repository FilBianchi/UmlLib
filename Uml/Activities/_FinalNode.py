from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Activities._ControlNode import ControlNode

class FinalNode(ControlNode):
    """UML metaclass FinalNode."""
    __spec__ = SPECIFICATIONS['FinalNode']
