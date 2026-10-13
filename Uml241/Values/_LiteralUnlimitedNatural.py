from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Values._LiteralSpecification import LiteralSpecification

class LiteralUnlimitedNatural(LiteralSpecification):
    """UML metaclass LiteralUnlimitedNatural."""
    __spec__ = SPECIFICATIONS['LiteralUnlimitedNatural']
    value: int | None
    def isComputable(self, *args, **kwargs):
        try:
            return _operation(self, 'LiteralUnlimitedNatural', 'isComputable', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def unlimitedValue(self, *args, **kwargs):
        try:
            return _operation(self, 'LiteralUnlimitedNatural', 'unlimitedValue', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
