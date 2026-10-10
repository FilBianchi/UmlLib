from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._NamedElement import NamedElement

class GeneralOrdering(NamedElement):
    """UML metaclass GeneralOrdering."""
    __spec__ = SPECIFICATIONS['GeneralOrdering']
    after: OccurrenceSpecification | None
    before: OccurrenceSpecification | None
