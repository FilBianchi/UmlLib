from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Values._LiteralSpecification import LiteralSpecification

class LiteralReal(LiteralSpecification):
    """UML metaclass LiteralReal."""
    __spec__ = SPECIFICATIONS['LiteralReal']
    value: float | None
    def isComputable(self, *args, **kwargs):
        try:
            return _operation(self, 'LiteralReal', 'isComputable', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def realValue(self, *args, **kwargs):
        try:
            return _operation(self, 'LiteralReal', 'realValue', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
