from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._NamedElement import NamedElement

class Trigger(NamedElement):
    """UML metaclass Trigger."""
    __spec__ = SPECIFICATIONS['Trigger']
    event: Event | None
    port: list[Port]
