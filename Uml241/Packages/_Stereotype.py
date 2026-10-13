from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..StructuredClassifiers._Class import Class

class Stereotype(Class):
    """UML metaclass Stereotype."""
    __spec__ = SPECIFICATIONS['Stereotype']
    icon: list[Image]
    profile: Profile | None
    def containingProfile(self, *args, **kwargs):
        try:
            return _operation(self, 'Stereotype', 'containingProfile', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
