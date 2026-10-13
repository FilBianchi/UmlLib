from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Classification._RedefinableElement import RedefinableElement

class Feature(RedefinableElement):
    """UML metaclass Feature."""
    __spec__ = SPECIFICATIONS['Feature']
    featuringClassifier: list[Classifier]
    isStatic: bool | None
