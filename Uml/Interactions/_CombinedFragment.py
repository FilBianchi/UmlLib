from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Interactions._InteractionFragment import InteractionFragment

class CombinedFragment(InteractionFragment):
    """UML metaclass CombinedFragment."""
    __spec__ = SPECIFICATIONS['CombinedFragment']
    cfragmentGate: list[Gate]
    interactionOperator: InteractionOperatorKind | None
    operand: list[InteractionOperand]
