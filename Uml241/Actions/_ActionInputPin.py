from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._InputPin import InputPin

class ActionInputPin(InputPin):
    """UML metaclass ActionInputPin."""
    __spec__ = SPECIFICATIONS['ActionInputPin']
    fromAction: Action | None
