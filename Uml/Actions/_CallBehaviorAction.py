from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._CallAction import CallAction

class CallBehaviorAction(CallAction):
    """UML metaclass CallBehaviorAction."""
    __spec__ = SPECIFICATIONS['CallBehaviorAction']
    behavior: Behavior | None
    def outputParameters(self, *args, **kwargs):
        try:
            return _operation(self, 'CallBehaviorAction', 'outputParameters', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def inputParameters(self, *args, **kwargs):
        try:
            return _operation(self, 'CallBehaviorAction', 'inputParameters', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
