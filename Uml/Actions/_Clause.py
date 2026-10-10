from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
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
