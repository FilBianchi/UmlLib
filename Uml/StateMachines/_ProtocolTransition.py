from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..StateMachines._Transition import Transition

class ProtocolTransition(Transition):
    """UML metaclass ProtocolTransition."""
    __spec__ = SPECIFICATIONS['ProtocolTransition']
    postCondition: Constraint | None
    preCondition: Constraint | None
    referred: list[Operation]
