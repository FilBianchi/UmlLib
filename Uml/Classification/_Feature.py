from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Classification._RedefinableElement import RedefinableElement

class Feature(RedefinableElement):
    """UML metaclass Feature."""
    __spec__ = SPECIFICATIONS['Feature']
    featuringClassifier: Classifier | None
    isStatic: bool | None
