from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Values._Observation import Observation

class DurationObservation(Observation):
    """UML metaclass DurationObservation."""
    __spec__ = SPECIFICATIONS['DurationObservation']
    event: list[NamedElement]
    firstEvent: list[bool]
