from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..SimpleClassifiers._BehavioredClassifier import BehavioredClassifier
from ..StructuredClassifiers._EncapsulatedClassifier import EncapsulatedClassifier

class Class(BehavioredClassifier, EncapsulatedClassifier):
    """UML metaclass Class."""
    __spec__ = SPECIFICATIONS['Class']
    extension: list[Extension]
    isAbstract: bool | None
    isActive: bool | None
    nestedClassifier: list[Classifier]
    ownedAttribute: list[Property]
    ownedOperation: list[Operation]
    ownedReception: list[Reception]
    superClass: list[Class]
