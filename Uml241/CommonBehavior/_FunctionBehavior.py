from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonBehavior._OpaqueBehavior import OpaqueBehavior

class FunctionBehavior(OpaqueBehavior):
    """UML metaclass FunctionBehavior."""
    __spec__ = SPECIFICATIONS['FunctionBehavior']
