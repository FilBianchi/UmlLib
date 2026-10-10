from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._Element import Element

class NamedElement(Element):
    """UML metaclass NamedElement."""
    __spec__ = SPECIFICATIONS['NamedElement']
    clientDependency: list[Dependency]
    name: str | None
    nameExpression: StringExpression | None
    namespace: Namespace | None
    qualifiedName: str | None
    visibility: VisibilityKind | None
    def allNamespaces(self, *args, **kwargs):
        try:
            return _operation(self, 'NamedElement', 'allNamespaces', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def allOwningPackages(self, *args, **kwargs):
        try:
            return _operation(self, 'NamedElement', 'allOwningPackages', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isDistinguishableFrom(self, *args, **kwargs):
        try:
            return _operation(self, 'NamedElement', 'isDistinguishableFrom', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def separator(self, *args, **kwargs):
        try:
            return _operation(self, 'NamedElement', 'separator', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
