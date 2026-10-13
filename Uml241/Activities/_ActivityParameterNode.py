from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Activities._ObjectNode import ObjectNode

class ActivityParameterNode(ObjectNode):
    """UML metaclass ActivityParameterNode."""
    __spec__ = SPECIFICATIONS['ActivityParameterNode']
    parameter: Parameter | None
