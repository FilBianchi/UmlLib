from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
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
    def allActions(self, *args, **kwargs):
        try:
            return _operation(self, 'LoopNode', 'allActions', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def sourceNodes(self, *args, **kwargs):
        try:
            return _operation(self, 'LoopNode', 'sourceNodes', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
