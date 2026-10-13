from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonBehavior._Behavior import Behavior

class Activity(Behavior):
    """UML metaclass Activity."""
    __spec__ = SPECIFICATIONS['Activity']
    edge: list[ActivityEdge]
    group: list[ActivityGroup]
    isReadOnly: bool | None
    isSingleExecution: bool | None
    node: list[ActivityNode]
    partition: list[ActivityPartition]
    structuredNode: list[StructuredActivityNode]
    variable: list[Variable]
