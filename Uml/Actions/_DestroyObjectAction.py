from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._Action import Action

class DestroyObjectAction(Action):
    """UML metaclass DestroyObjectAction."""
    __spec__ = SPECIFICATIONS['DestroyObjectAction']
    isDestroyLinks: bool | None
    isDestroyOwnedObjects: bool | None
    target: InputPin | None
