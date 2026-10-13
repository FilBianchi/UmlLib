from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..StructuredClassifiers._StructuredClassifier import StructuredClassifier

class EncapsulatedClassifier(StructuredClassifier):
    """UML metaclass EncapsulatedClassifier."""
    __spec__ = SPECIFICATIONS['EncapsulatedClassifier']
    ownedPort: list[Port]
