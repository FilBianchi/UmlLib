from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Classification._RedefinableElement import RedefinableElement

class Vertex(RedefinableElement):
    """UML metaclass Vertex."""
    __spec__ = SPECIFICATIONS['Vertex']
    container: Region | None
    incoming: list[Transition]
    outgoing: list[Transition]
    redefinitionContext: Classifier | None
    redefinedVertex: Vertex | None
    def containingStateMachine(self, *args, **kwargs):
        try:
            return _operation(self, 'Vertex', 'containingStateMachine', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isContainedInState(self, *args, **kwargs):
        try:
            return _operation(self, 'Vertex', 'isContainedInState', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isContainedInRegion(self, *args, **kwargs):
        try:
            return _operation(self, 'Vertex', 'isContainedInRegion', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isConsistentWith(self, *args, **kwargs):
        try:
            return _operation(self, 'Vertex', 'isConsistentWith', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
