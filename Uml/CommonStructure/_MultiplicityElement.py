from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._Element import Element

class MultiplicityElement(Element):
    """UML metaclass MultiplicityElement."""
    __spec__ = SPECIFICATIONS['MultiplicityElement']
    isOrdered: bool | None
    isUnique: bool | None
    lower: int | None
    lowerValue: ValueSpecification | None
    upper: int | None
    upperValue: ValueSpecification | None
    def compatibleWith(self, *args, **kwargs):
        try:
            return _operation(self, 'MultiplicityElement', 'compatibleWith', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def includesMultiplicity(self, *args, **kwargs):
        try:
            return _operation(self, 'MultiplicityElement', 'includesMultiplicity', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def is_(self, *args, **kwargs):
        try:
            return _operation(self, 'MultiplicityElement', 'is', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isMultivalued(self, *args, **kwargs):
        try:
            return _operation(self, 'MultiplicityElement', 'isMultivalued', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def lowerBound(self, *args, **kwargs):
        try:
            return _operation(self, 'MultiplicityElement', 'lowerBound', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def upperBound(self, *args, **kwargs):
        try:
            return _operation(self, 'MultiplicityElement', 'upperBound', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
