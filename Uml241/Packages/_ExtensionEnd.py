from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
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
