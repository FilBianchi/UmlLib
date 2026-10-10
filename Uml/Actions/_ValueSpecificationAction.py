from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._Action import Action

class ValueSpecificationAction(Action):
    """UML metaclass ValueSpecificationAction."""
    __spec__ = SPECIFICATIONS['ValueSpecificationAction']
    result: OutputPin | None
    value: ValueSpecification | None
