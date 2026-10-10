from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
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
