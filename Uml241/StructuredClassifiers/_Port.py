from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Classification._Property import Property

class Port(Property):
    """UML metaclass Port."""
    __spec__ = SPECIFICATIONS['Port']
    isBehavior: bool | None
    isConjugated: bool | None
    isService: bool | None
    protocol: ProtocolStateMachine | None
    provided: list[Interface]
    redefinedPort: list[Port]
    required: list[Interface]
