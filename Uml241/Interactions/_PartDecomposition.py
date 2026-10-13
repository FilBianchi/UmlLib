from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Interactions._InteractionUse import InteractionUse

class PartDecomposition(InteractionUse):
    """UML metaclass PartDecomposition."""
    __spec__ = SPECIFICATIONS['PartDecomposition']
