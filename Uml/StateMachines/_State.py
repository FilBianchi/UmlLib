from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._Namespace import Namespace
from ..StateMachines._Vertex import Vertex

class State(Namespace, Vertex):
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
