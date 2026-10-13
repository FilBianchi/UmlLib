from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._NamedElement import NamedElement

class GeneralOrdering(NamedElement):
    """UML metaclass GeneralOrdering."""
    __spec__ = SPECIFICATIONS['GeneralOrdering']
    after: OccurrenceSpecification | None
    before: OccurrenceSpecification | None
