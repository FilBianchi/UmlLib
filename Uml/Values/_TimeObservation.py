from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Values._Observation import Observation

class TimeObservation(Observation):
    """UML metaclass TimeObservation."""
    __spec__ = SPECIFICATIONS['TimeObservation']
    event: NamedElement | None
    firstEvent: bool | None
