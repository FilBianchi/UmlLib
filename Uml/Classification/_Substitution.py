from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._Realization import Realization

class Substitution(Realization):
    """UML metaclass Substitution."""
    __spec__ = SPECIFICATIONS['Substitution']
    contract: Classifier | None
    substitutingClassifier: Classifier | None
