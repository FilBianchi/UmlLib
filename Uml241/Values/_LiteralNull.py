from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Values._LiteralSpecification import LiteralSpecification

class LiteralNull(LiteralSpecification):
    """UML metaclass LiteralNull."""
    __spec__ = SPECIFICATIONS['LiteralNull']
    def isComputable(self, *args, **kwargs):
        try:
            return _operation(self, 'LiteralNull', 'isComputable', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isNull(self, *args, **kwargs):
        try:
            return _operation(self, 'LiteralNull', 'isNull', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
