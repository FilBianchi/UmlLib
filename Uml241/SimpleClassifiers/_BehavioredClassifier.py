from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Classification._Classifier import Classifier

class BehavioredClassifier(Classifier):
    """UML metaclass BehavioredClassifier."""
    __spec__ = SPECIFICATIONS['BehavioredClassifier']
    classifierBehavior: Behavior | None
    interfaceRealization: list[InterfaceRealization]
    ownedBehavior: list[Behavior]
