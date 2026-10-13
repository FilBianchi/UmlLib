from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._Namespace import Namespace
from ..Activities._ActivityGroup import ActivityGroup
from ..Actions._Action import Action

class StructuredActivityNode(Namespace, ActivityGroup, Action):
    """UML metaclass StructuredActivityNode."""
    __spec__ = SPECIFICATIONS['StructuredActivityNode']
    activity: Activity | None
    edge: list[ActivityEdge]
    mustIsolate: bool | None
    node: list[ActivityNode]
    structuredNodeInput: list[InputPin]
    structuredNodeOutput: list[OutputPin]
    variable: list[Variable]
