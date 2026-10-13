from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Interactions._InteractionFragment import InteractionFragment

class StateInvariant(InteractionFragment):
    """UML metaclass StateInvariant."""
    __spec__ = SPECIFICATIONS['StateInvariant']
    covered: Lifeline | None
    invariant: Constraint | None
