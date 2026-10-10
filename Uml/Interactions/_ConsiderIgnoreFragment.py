from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Interactions._CombinedFragment import CombinedFragment

class ConsiderIgnoreFragment(CombinedFragment):
    """UML metaclass ConsiderIgnoreFragment."""
    __spec__ = SPECIFICATIONS['ConsiderIgnoreFragment']
    message: list[NamedElement]
