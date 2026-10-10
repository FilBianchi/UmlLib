from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Interactions._MessageEnd import MessageEnd

class Gate(MessageEnd):
    """UML metaclass Gate."""
    __spec__ = SPECIFICATIONS['Gate']
    def isOutsideCF(self, *args, **kwargs):
        try:
            return _operation(self, 'Gate', 'isOutsideCF', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isInsideCF(self, *args, **kwargs):
        try:
            return _operation(self, 'Gate', 'isInsideCF', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isActual(self, *args, **kwargs):
        try:
            return _operation(self, 'Gate', 'isActual', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isFormal(self, *args, **kwargs):
        try:
            return _operation(self, 'Gate', 'isFormal', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def getName(self, *args, **kwargs):
        try:
            return _operation(self, 'Gate', 'getName', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def matches(self, *args, **kwargs):
        try:
            return _operation(self, 'Gate', 'matches', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isDistinguishableFrom(self, *args, **kwargs):
        try:
            return _operation(self, 'Gate', 'isDistinguishableFrom', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def getOperand(self, *args, **kwargs):
        try:
            return _operation(self, 'Gate', 'getOperand', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
