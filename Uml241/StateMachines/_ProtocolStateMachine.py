from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..StateMachines._StateMachine import StateMachine

class ProtocolStateMachine(StateMachine):
    """UML metaclass ProtocolStateMachine."""
    __spec__ = SPECIFICATIONS['ProtocolStateMachine']
    conformance: list[ProtocolConformance]
