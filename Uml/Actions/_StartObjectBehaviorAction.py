from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._CallAction import CallAction

class StartObjectBehaviorAction(CallAction):
    """UML metaclass StartObjectBehaviorAction."""
    __spec__ = SPECIFICATIONS['StartObjectBehaviorAction']
    object: InputPin | None
    def outputParameters(self, *args, **kwargs):
        try:
            return _operation(self, 'StartObjectBehaviorAction', 'outputParameters', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def inputParameters(self, *args, **kwargs):
        try:
            return _operation(self, 'StartObjectBehaviorAction', 'inputParameters', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def behavior(self, *args, **kwargs):
        try:
            return _operation(self, 'StartObjectBehaviorAction', 'behavior', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
