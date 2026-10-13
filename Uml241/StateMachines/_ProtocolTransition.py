from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..StateMachines._Transition import Transition

class ProtocolTransition(Transition):
    """UML metaclass ProtocolTransition."""
    __spec__ = SPECIFICATIONS['ProtocolTransition']
    postCondition: Constraint | None
    preCondition: Constraint | None
    referred: list[Operation]
