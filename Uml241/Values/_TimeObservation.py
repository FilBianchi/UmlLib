from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Values._Observation import Observation

class TimeObservation(Observation):
    """UML metaclass TimeObservation."""
    __spec__ = SPECIFICATIONS['TimeObservation']
    event: NamedElement | None
    firstEvent: bool | None
