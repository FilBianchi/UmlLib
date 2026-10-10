from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Interactions._InteractionFragment import InteractionFragment
from ..CommonStructure._Namespace import Namespace

class InteractionOperand(InteractionFragment, Namespace):
    """UML metaclass InteractionOperand."""
    __spec__ = SPECIFICATIONS['InteractionOperand']
    fragment: list[InteractionFragment]
    guard: InteractionConstraint | None
