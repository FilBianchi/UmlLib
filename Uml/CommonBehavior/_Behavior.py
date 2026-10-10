from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..StructuredClassifiers._Class import Class

class Behavior(Class):
    """UML metaclass Behavior."""
    __spec__ = SPECIFICATIONS['Behavior']
    context: BehavioredClassifier | None
    isReentrant: bool | None
    ownedParameter: list[Parameter]
    ownedParameterSet: list[ParameterSet]
    postcondition: list[Constraint]
    precondition: list[Constraint]
    specification: BehavioralFeature | None
    redefinedBehavior: list[Behavior]
    def behavioredClassifier(self, *args, **kwargs):
        try:
            return _operation(self, 'Behavior', 'behavioredClassifier', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def inputParameters(self, *args, **kwargs):
        try:
            return _operation(self, 'Behavior', 'inputParameters', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def outputParameters(self, *args, **kwargs):
        try:
            return _operation(self, 'Behavior', 'outputParameters', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
