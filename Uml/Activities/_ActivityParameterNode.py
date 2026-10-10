from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Activities._ObjectNode import ObjectNode

class ActivityParameterNode(ObjectNode):
    """UML metaclass ActivityParameterNode."""
    __spec__ = SPECIFICATIONS['ActivityParameterNode']
    parameter: Parameter | None
