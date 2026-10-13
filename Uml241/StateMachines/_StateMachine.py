from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonBehavior._Behavior import Behavior

class StateMachine(Behavior):
    """UML metaclass StateMachine."""
    __spec__ = SPECIFICATIONS['StateMachine']
    connectionPoint: list[Pseudostate]
    extendedStateMachine: list[StateMachine]
    region: list[Region]
    submachineState: list[State]
    def LCA(self, *args, **kwargs):
        try:
            return _operation(self, 'StateMachine', 'LCA', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def ancestor(self, *args, **kwargs):
        try:
            return _operation(self, 'StateMachine', 'ancestor', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isConsistentWith(self, *args, **kwargs):
        try:
            return _operation(self, 'StateMachine', 'isConsistentWith', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isRedefinitionContextValid(self, *args, **kwargs):
        try:
            return _operation(self, 'StateMachine', 'isRedefinitionContextValid', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
