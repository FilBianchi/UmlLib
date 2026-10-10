from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._Realization import Realization

class InterfaceRealization(Realization):
    """UML metaclass InterfaceRealization."""
    __spec__ = SPECIFICATIONS['InterfaceRealization']
    contract: Interface | None
    implementingClassifier: BehavioredClassifier | None
