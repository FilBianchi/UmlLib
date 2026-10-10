from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._Realization import Realization

class ComponentRealization(Realization):
    """UML metaclass ComponentRealization."""
    __spec__ = SPECIFICATIONS['ComponentRealization']
    abstraction: Component | None
    realizingClassifier: list[Classifier]
