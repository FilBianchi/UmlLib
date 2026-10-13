from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._NamedElement import NamedElement

class ParameterSet(NamedElement):
    """UML metaclass ParameterSet."""
    __spec__ = SPECIFICATIONS['ParameterSet']
    condition: list[Constraint]
    parameter: list[Parameter]
