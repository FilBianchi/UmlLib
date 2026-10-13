from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._Realization import Realization

class Substitution(Realization):
    """UML metaclass Substitution."""
    __spec__ = SPECIFICATIONS['Substitution']
    contract: Classifier | None
    substitutingClassifier: Classifier | None
