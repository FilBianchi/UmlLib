from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._NamedElement import NamedElement

class ParameterSet(NamedElement):
    """UML metaclass ParameterSet."""
    __spec__ = SPECIFICATIONS['ParameterSet']
    condition: list[Constraint]
    parameter: list[Parameter]
