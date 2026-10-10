from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Activities._ControlNode import ControlNode

class InitialNode(ControlNode):
    """UML metaclass InitialNode."""
    __spec__ = SPECIFICATIONS['InitialNode']
