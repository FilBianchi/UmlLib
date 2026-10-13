from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Interactions._InteractionFragment import InteractionFragment
from ..CommonBehavior._Behavior import Behavior

class Interaction(InteractionFragment, Behavior):
    """UML metaclass Interaction."""
    __spec__ = SPECIFICATIONS['Interaction']
    action: list[Action]
    formalGate: list[Gate]
    fragment: list[InteractionFragment]
    lifeline: list[Lifeline]
    message: list[Message]
