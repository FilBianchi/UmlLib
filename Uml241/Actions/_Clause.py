from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._Element import Element

class Clause(Element):
    """UML metaclass Clause."""
    __spec__ = SPECIFICATIONS['Clause']
    body: list[ExecutableNode]
    bodyOutput: list[OutputPin]
    decider: OutputPin | None
    predecessorClause: list[Clause]
    successorClause: list[Clause]
    test: list[ExecutableNode]
