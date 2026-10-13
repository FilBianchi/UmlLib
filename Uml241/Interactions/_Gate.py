from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Interactions._MessageEnd import MessageEnd

class Gate(MessageEnd):
    """UML metaclass Gate."""
    __spec__ = SPECIFICATIONS['Gate']
