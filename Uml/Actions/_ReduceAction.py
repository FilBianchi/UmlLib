from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._Action import Action

class ReduceAction(Action):
    """UML metaclass ReduceAction."""
    __spec__ = SPECIFICATIONS['ReduceAction']
    collection: InputPin | None
    isOrdered: bool | None
    reducer: Behavior | None
    result: OutputPin | None
