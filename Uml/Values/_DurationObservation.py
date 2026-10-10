from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Values._Observation import Observation

class DurationObservation(Observation):
    """UML metaclass DurationObservation."""
    __spec__ = SPECIFICATIONS['DurationObservation']
    event: list[NamedElement]
    firstEvent: list[bool]
