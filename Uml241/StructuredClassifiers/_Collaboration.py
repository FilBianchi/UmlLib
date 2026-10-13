from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..StructuredClassifiers._StructuredClassifier import StructuredClassifier
from ..SimpleClassifiers._BehavioredClassifier import BehavioredClassifier

class Collaboration(StructuredClassifier, BehavioredClassifier):
    """UML metaclass Collaboration."""
    __spec__ = SPECIFICATIONS['Collaboration']
    collaborationRole: list[ConnectableElement]
