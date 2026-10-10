from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Classification._Classifier import Classifier

class BehavioredClassifier(Classifier):
    """UML metaclass BehavioredClassifier."""
    __spec__ = SPECIFICATIONS['BehavioredClassifier']
    classifierBehavior: Behavior | None
    interfaceRealization: list[InterfaceRealization]
    ownedBehavior: list[Behavior]
