from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._MultiplicityElement import MultiplicityElement
from ..StructuredClassifiers._ConnectableElement import ConnectableElement

class Parameter(MultiplicityElement, ConnectableElement):
    """UML metaclass Parameter."""
    __spec__ = SPECIFICATIONS['Parameter']
    default: str | None
    defaultValue: ValueSpecification | None
    direction: ParameterDirectionKind | None
    effect: ParameterEffectKind | None
    isException: bool | None
    isStream: bool | None
    operation: Operation | None
    parameterSet: list[ParameterSet]
