from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._PackageableElement import PackageableElement

class GeneralizationSet(PackageableElement):
    """UML metaclass GeneralizationSet."""
    __spec__ = SPECIFICATIONS['GeneralizationSet']
    generalization: list[Generalization]
    isCovering: bool | None
    isDisjoint: bool | None
    powertype: Classifier | None
