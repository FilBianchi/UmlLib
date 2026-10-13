from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
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
    redefinedBehavior: list[Behavior]
    specification: BehavioralFeature | None
