from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Values._LiteralSpecification import LiteralSpecification

class LiteralString(LiteralSpecification):
    """UML metaclass LiteralString."""
    __spec__ = SPECIFICATIONS['LiteralString']
    value: str | None
    def isComputable(self, *args, **kwargs):
        try:
            return _operation(self, 'LiteralString', 'isComputable', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def stringValue(self, *args, **kwargs):
        try:
            return _operation(self, 'LiteralString', 'stringValue', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
