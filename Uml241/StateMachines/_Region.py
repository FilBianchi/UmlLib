from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._Namespace import Namespace
from ..Classification._RedefinableElement import RedefinableElement

class Region(Namespace, RedefinableElement):
    """UML metaclass Region."""
    __spec__ = SPECIFICATIONS['Region']
    extendedRegion: Region | None
    redefinitionContext: Classifier | None
    state: State | None
    stateMachine: StateMachine | None
    subvertex: list[Vertex]
    transition: list[Transition]
    def belongsToPSM(self, *args, **kwargs):
        try:
            return _operation(self, 'Region', 'belongsToPSM', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def containingStateMachine(self, *args, **kwargs):
        try:
            return _operation(self, 'Region', 'containingStateMachine', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isConsistentWith(self, *args, **kwargs):
        try:
            return _operation(self, 'Region', 'isConsistentWith', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isRedefinitionContextValid(self, *args, **kwargs):
        try:
            return _operation(self, 'Region', 'isRedefinitionContextValid', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
