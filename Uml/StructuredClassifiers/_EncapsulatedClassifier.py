from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..StructuredClassifiers._StructuredClassifier import StructuredClassifier

class EncapsulatedClassifier(StructuredClassifier):
    """UML metaclass EncapsulatedClassifier."""
    __spec__ = SPECIFICATIONS['EncapsulatedClassifier']
    ownedPort: list[Port]
