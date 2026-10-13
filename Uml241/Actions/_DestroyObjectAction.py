from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._Action import Action

class DestroyObjectAction(Action):
    """UML metaclass DestroyObjectAction."""
    __spec__ = SPECIFICATIONS['DestroyObjectAction']
    isDestroyLinks: bool | None
    isDestroyOwnedObjects: bool | None
    target: InputPin | None
