from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Activities._ExecutableNode import ExecutableNode

class Action(ExecutableNode):
    """UML metaclass Action."""
    __spec__ = SPECIFICATIONS['Action']
    context: Classifier | None
    input: list[InputPin]
    isLocallyReentrant: bool | None
    localPostcondition: list[Constraint]
    localPrecondition: list[Constraint]
    output: list[OutputPin]
    def allActions(self, *args, **kwargs):
        try:
            return _operation(self, 'Action', 'allActions', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def allOwnedNodes(self, *args, **kwargs):
        try:
            return _operation(self, 'Action', 'allOwnedNodes', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def containingBehavior(self, *args, **kwargs):
        try:
            return _operation(self, 'Action', 'containingBehavior', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
