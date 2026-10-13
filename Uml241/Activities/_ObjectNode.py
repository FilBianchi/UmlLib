from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
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
