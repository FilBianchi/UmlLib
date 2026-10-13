from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._Realization import Realization

class ComponentRealization(Realization):
    """UML metaclass ComponentRealization."""
    __spec__ = SPECIFICATIONS['ComponentRealization']
    abstraction: Component | None
    realizingClassifier: list[Classifier]
