from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._Namespace import Namespace
from ..Classification._RedefinableElement import RedefinableElement

class Transition(Namespace, RedefinableElement):
    """UML metaclass Transition."""
    __spec__ = SPECIFICATIONS['Transition']
    container: Region | None
    effect: Behavior | None
    guard: Constraint | None
    kind: TransitionKind | None
    redefinedTransition: Transition | None
    redefinitionContext: Classifier | None
    source: Vertex | None
    target: Vertex | None
    trigger: list[Trigger]
    def containingStateMachine(self, *args, **kwargs):
        try:
            return _operation(self, 'Transition', 'containingStateMachine', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isConsistentWith(self, *args, **kwargs):
        try:
            return _operation(self, 'Transition', 'isConsistentWith', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
