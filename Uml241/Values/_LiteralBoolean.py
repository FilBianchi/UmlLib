from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Values._LiteralSpecification import LiteralSpecification

class LiteralBoolean(LiteralSpecification):
    """UML metaclass LiteralBoolean."""
    __spec__ = SPECIFICATIONS['LiteralBoolean']
    value: bool | None
    def booleanValue(self, *args, **kwargs):
        try:
            return _operation(self, 'LiteralBoolean', 'booleanValue', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isComputable(self, *args, **kwargs):
        try:
            return _operation(self, 'LiteralBoolean', 'isComputable', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
