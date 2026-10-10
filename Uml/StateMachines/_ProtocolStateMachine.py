from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..StateMachines._StateMachine import StateMachine

class ProtocolStateMachine(StateMachine):
    """UML metaclass ProtocolStateMachine."""
    __spec__ = SPECIFICATIONS['ProtocolStateMachine']
    conformance: list[ProtocolConformance]
