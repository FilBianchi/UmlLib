from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..SimpleClassifiers._BehavioredClassifier import BehavioredClassifier

class Actor(BehavioredClassifier):
    """UML metaclass Actor."""
    __spec__ = SPECIFICATIONS['Actor']
