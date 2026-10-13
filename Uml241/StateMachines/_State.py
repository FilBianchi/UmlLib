from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Classification._RedefinableElement import RedefinableElement
from ..CommonStructure._Namespace import Namespace
from ..StateMachines._Vertex import Vertex

class State(RedefinableElement, Namespace, Vertex):
    """UML metaclass State."""
    __spec__ = SPECIFICATIONS['State']
    connection: list[ConnectionPointReference]
    connectionPoint: list[Pseudostate]
    deferrableTrigger: list[Trigger]
    doActivity: Behavior | None
    entry: Behavior | None
    exit: Behavior | None
    isComposite: bool | None
    isOrthogonal: bool | None
    isSimple: bool | None
    isSubmachineState: bool | None
    redefinedState: State | None
    redefinitionContext: Classifier | None
    region: list[Region]
    stateInvariant: Constraint | None
    submachine: StateMachine | None
    def containingStateMachine(self, *args, **kwargs):
        try:
            return _operation(self, 'State', 'containingStateMachine', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isConsistentWith(self, *args, **kwargs):
        try:
            return _operation(self, 'State', 'isConsistentWith', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isRedefinitionContextValid(self, *args, **kwargs):
        try:
            return _operation(self, 'State', 'isRedefinitionContextValid', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
