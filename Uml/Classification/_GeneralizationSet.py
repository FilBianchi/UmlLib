from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._PackageableElement import PackageableElement

class GeneralizationSet(PackageableElement):
    """UML metaclass GeneralizationSet."""
    __spec__ = SPECIFICATIONS['GeneralizationSet']
    generalization: list[Generalization]
    isCovering: bool | None
    isDisjoint: bool | None
    powertype: Classifier | None
