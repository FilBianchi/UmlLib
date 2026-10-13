from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..StructuredClassifiers._Association import Association

class Extension(Association):
    """UML metaclass Extension."""
    __spec__ = SPECIFICATIONS['Extension']
    isRequired: bool | None
    metaclass: Class | None
    ownedEnd: ExtensionEnd | None
    def metaclassEnd(self, *args, **kwargs):
        try:
            return _operation(self, 'Extension', 'metaclassEnd', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
