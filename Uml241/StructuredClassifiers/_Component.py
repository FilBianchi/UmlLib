from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..StructuredClassifiers._Class import Class

class Component(Class):
    """UML metaclass Component."""
    __spec__ = SPECIFICATIONS['Component']
    isIndirectlyInstantiated: bool | None
    packagedElement: list[PackageableElement]
    provided: list[Interface]
    realization: list[ComponentRealization]
    required: list[Interface]
    def realizedInterfaces(self, *args, **kwargs):
        try:
            return _operation(self, 'Component', 'realizedInterfaces', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def usedInterfaces(self, *args, **kwargs):
        try:
            return _operation(self, 'Component', 'usedInterfaces', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
