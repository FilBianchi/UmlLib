from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
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
    def inherit(self, *args, **kwargs):
        try:
            return _operation(self, 'Class', 'inherit', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
