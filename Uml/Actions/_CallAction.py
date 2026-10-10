from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._InvocationAction import InvocationAction

class CallAction(InvocationAction):
    """UML metaclass CallAction."""
    __spec__ = SPECIFICATIONS['CallAction']
    isSynchronous: bool | None
    result: list[OutputPin]
    def inputParameters(self, *args, **kwargs):
        try:
            return _operation(self, 'CallAction', 'inputParameters', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def outputParameters(self, *args, **kwargs):
        try:
            return _operation(self, 'CallAction', 'outputParameters', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
