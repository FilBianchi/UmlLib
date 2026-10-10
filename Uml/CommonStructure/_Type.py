from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._PackageableElement import PackageableElement

class Type(PackageableElement):
    """UML metaclass Type."""
    __spec__ = SPECIFICATIONS['Type']
    package: Package | None
    def conformsTo(self, *args, **kwargs):
        try:
            return _operation(self, 'Type', 'conformsTo', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
