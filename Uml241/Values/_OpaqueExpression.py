from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Values._ValueSpecification import ValueSpecification

class OpaqueExpression(ValueSpecification):
    """UML metaclass OpaqueExpression."""
    __spec__ = SPECIFICATIONS['OpaqueExpression']
    behavior: Behavior | None
    body: list[str]
    language: list[str]
    result: Parameter | None
    def isIntegral(self, *args, **kwargs):
        try:
            return _operation(self, 'OpaqueExpression', 'isIntegral', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isNonNegative(self, *args, **kwargs):
        try:
            return _operation(self, 'OpaqueExpression', 'isNonNegative', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isPositive(self, *args, **kwargs):
        try:
            return _operation(self, 'OpaqueExpression', 'isPositive', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def value(self, *args, **kwargs):
        try:
            return _operation(self, 'OpaqueExpression', 'value', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
