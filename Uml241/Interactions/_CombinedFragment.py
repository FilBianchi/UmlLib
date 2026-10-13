from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Interactions._InteractionFragment import InteractionFragment

class CombinedFragment(InteractionFragment):
    """UML metaclass CombinedFragment."""
    __spec__ = SPECIFICATIONS['CombinedFragment']
    cfragmentGate: list[Gate]
    interactionOperator: InteractionOperatorKind | None
    operand: list[InteractionOperand]
