from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..SimpleClassifiers._BehavioredClassifier import BehavioredClassifier

class UseCase(BehavioredClassifier):
    """UML metaclass UseCase."""
    __spec__ = SPECIFICATIONS['UseCase']
    extend: list[Extend]
    extensionPoint: list[ExtensionPoint]
    include: list[Include]
    subject: list[Classifier]
    def allIncludedUseCases(self, *args, **kwargs):
        try:
            return _operation(self, 'UseCase', 'allIncludedUseCases', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
