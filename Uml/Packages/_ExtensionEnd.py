from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Classification._Property import Property

class ExtensionEnd(Property):
    """UML metaclass ExtensionEnd."""
    __spec__ = SPECIFICATIONS['ExtensionEnd']
    lower: int | None
    type: Stereotype | None
    def lowerBound(self, *args, **kwargs):
        try:
            return _operation(self, 'ExtensionEnd', 'lowerBound', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
