from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonBehavior._Event import Event

class ChangeEvent(Event):
    """UML metaclass ChangeEvent."""
    __spec__ = SPECIFICATIONS['ChangeEvent']
    changeExpression: ValueSpecification | None
