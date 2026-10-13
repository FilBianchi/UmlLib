from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._StructuredActivityNode import StructuredActivityNode

class LoopNode(StructuredActivityNode):
    """UML metaclass LoopNode."""
    __spec__ = SPECIFICATIONS['LoopNode']
    bodyOutput: list[OutputPin]
    bodyPart: list[ExecutableNode]
    decider: OutputPin | None
    isTestedFirst: bool | None
    loopVariable: list[OutputPin]
    loopVariableInput: list[InputPin]
    result: list[OutputPin]
    setupPart: list[ExecutableNode]
    test: list[ExecutableNode]
