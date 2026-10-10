from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..StructuredClassifiers._StructuredClassifier import StructuredClassifier
from ..SimpleClassifiers._BehavioredClassifier import BehavioredClassifier

class Collaboration(StructuredClassifier, BehavioredClassifier):
    """UML metaclass Collaboration."""
    __spec__ = SPECIFICATIONS['Collaboration']
    collaborationRole: list[ConnectableElement]
