from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Interactions._InteractionUse import InteractionUse

class PartDecomposition(InteractionUse):
    """UML metaclass PartDecomposition."""
    __spec__ = SPECIFICATIONS['PartDecomposition']
