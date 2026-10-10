from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Interactions._InteractionFragment import InteractionFragment

class StateInvariant(InteractionFragment):
    """UML metaclass StateInvariant."""
    __spec__ = SPECIFICATIONS['StateInvariant']
    covered: Lifeline | None
    invariant: Constraint | None
