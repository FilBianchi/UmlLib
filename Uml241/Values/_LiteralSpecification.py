from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Values._ValueSpecification import ValueSpecification

class LiteralSpecification(ValueSpecification):
    """UML metaclass LiteralSpecification."""
    __spec__ = SPECIFICATIONS['LiteralSpecification']
