from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..StateMachines._State import State

class FinalState(State):
    """UML metaclass FinalState."""
    __spec__ = SPECIFICATIONS['FinalState']
