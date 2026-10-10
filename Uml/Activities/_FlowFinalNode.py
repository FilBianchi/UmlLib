from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Activities._FinalNode import FinalNode

class FlowFinalNode(FinalNode):
    """UML metaclass FlowFinalNode."""
    __spec__ = SPECIFICATIONS['FlowFinalNode']
