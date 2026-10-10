from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
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
    def basicProvided(self, *args, **kwargs):
        try:
            return _operation(self, 'Port', 'basicProvided', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def basicRequired(self, *args, **kwargs):
        try:
            return _operation(self, 'Port', 'basicRequired', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
