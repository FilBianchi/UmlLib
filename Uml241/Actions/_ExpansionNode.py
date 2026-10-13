from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Activities._ObjectNode import ObjectNode

class ExpansionNode(ObjectNode):
    """UML metaclass ExpansionNode."""
    __spec__ = SPECIFICATIONS['ExpansionNode']
    regionAsInput: ExpansionRegion | None
    regionAsOutput: ExpansionRegion | None
