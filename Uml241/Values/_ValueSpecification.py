from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._TypedElement import TypedElement
from ..CommonStructure._PackageableElement import PackageableElement

class ValueSpecification(TypedElement, PackageableElement):
    """UML metaclass ValueSpecification."""
    __spec__ = SPECIFICATIONS['ValueSpecification']
    def booleanValue(self, *args, **kwargs):
        try:
            return _operation(self, 'ValueSpecification', 'booleanValue', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def integerValue(self, *args, **kwargs):
        try:
            return _operation(self, 'ValueSpecification', 'integerValue', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isCompatibleWith(self, *args, **kwargs):
        try:
            return _operation(self, 'ValueSpecification', 'isCompatibleWith', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isComputable(self, *args, **kwargs):
        try:
            return _operation(self, 'ValueSpecification', 'isComputable', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isNull(self, *args, **kwargs):
        try:
            return _operation(self, 'ValueSpecification', 'isNull', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def realValue(self, *args, **kwargs):
        try:
            return _operation(self, 'ValueSpecification', 'realValue', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def stringValue(self, *args, **kwargs):
        try:
            return _operation(self, 'ValueSpecification', 'stringValue', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def unlimitedValue(self, *args, **kwargs):
        try:
            return _operation(self, 'ValueSpecification', 'unlimitedValue', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
