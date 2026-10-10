from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._AcceptEventAction import AcceptEventAction

class AcceptCallAction(AcceptEventAction):
    """UML metaclass AcceptCallAction."""
    __spec__ = SPECIFICATIONS['AcceptCallAction']
    returnInformation: OutputPin | None
