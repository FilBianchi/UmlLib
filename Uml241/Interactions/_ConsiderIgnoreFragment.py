from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Interactions._CombinedFragment import CombinedFragment

class ConsiderIgnoreFragment(CombinedFragment):
    """UML metaclass ConsiderIgnoreFragment."""
    __spec__ = SPECIFICATIONS['ConsiderIgnoreFragment']
    message: list[NamedElement]
