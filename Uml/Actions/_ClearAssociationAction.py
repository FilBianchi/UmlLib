from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._Action import Action

class ClearAssociationAction(Action):
    """UML metaclass ClearAssociationAction."""
    __spec__ = SPECIFICATIONS['ClearAssociationAction']
    association: Association | None
    object: InputPin | None
