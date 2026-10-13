from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._Realization import Realization

class InterfaceRealization(Realization):
    """UML metaclass InterfaceRealization."""
    __spec__ = SPECIFICATIONS['InterfaceRealization']
    contract: Interface | None
    implementingClassifier: BehavioredClassifier | None
