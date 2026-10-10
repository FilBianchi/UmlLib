from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Values._LiteralSpecification import LiteralSpecification

class LiteralInteger(LiteralSpecification):
    """UML metaclass LiteralInteger."""
    __spec__ = SPECIFICATIONS['LiteralInteger']
    value: int | None
    def integerValue(self, *args, **kwargs):
        try:
            return _operation(self, 'LiteralInteger', 'integerValue', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isComputable(self, *args, **kwargs):
        try:
            return _operation(self, 'LiteralInteger', 'isComputable', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
