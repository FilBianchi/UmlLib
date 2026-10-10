from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._TypedElement import TypedElement
from ..Activities._ActivityNode import ActivityNode

class ObjectNode(TypedElement, ActivityNode):
    """UML metaclass ObjectNode."""
    __spec__ = SPECIFICATIONS['ObjectNode']
    inState: list[State]
    isControlType: bool | None
    ordering: ObjectNodeOrderingKind | None
    selection: Behavior | None
    upperBound: ValueSpecification | None
