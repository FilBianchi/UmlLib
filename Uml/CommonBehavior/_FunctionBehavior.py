from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonBehavior._OpaqueBehavior import OpaqueBehavior

class FunctionBehavior(OpaqueBehavior):
    """UML metaclass FunctionBehavior."""
    __spec__ = SPECIFICATIONS['FunctionBehavior']
    def hasAllDataTypeAttributes(self, *args, **kwargs):
        try:
            return _operation(self, 'FunctionBehavior', 'hasAllDataTypeAttributes', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
