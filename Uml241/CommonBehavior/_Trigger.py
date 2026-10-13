from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._NamedElement import NamedElement

class Trigger(NamedElement):
    """UML metaclass Trigger."""
    __spec__ = SPECIFICATIONS['Trigger']
    event: Event | None
    port: list[Port]
