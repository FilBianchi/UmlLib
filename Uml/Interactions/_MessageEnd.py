from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._NamedElement import NamedElement

class MessageEnd(NamedElement):
    """UML metaclass MessageEnd."""
    __spec__ = SPECIFICATIONS['MessageEnd']
    message: Message | None
    def oppositeEnd(self, *args, **kwargs):
        try:
            return _operation(self, 'MessageEnd', 'oppositeEnd', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isSend(self, *args, **kwargs):
        try:
            return _operation(self, 'MessageEnd', 'isSend', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isReceive(self, *args, **kwargs):
        try:
            return _operation(self, 'MessageEnd', 'isReceive', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def enclosingFragment(self, *args, **kwargs):
        try:
            return _operation(self, 'MessageEnd', 'enclosingFragment', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
