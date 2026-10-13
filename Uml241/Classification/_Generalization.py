from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._DirectedRelationship import DirectedRelationship

class Generalization(DirectedRelationship):
    """UML metaclass Generalization."""
    __spec__ = SPECIFICATIONS['Generalization']
    general: Classifier | None
    generalizationSet: list[GeneralizationSet]
    isSubstitutable: bool | None
    specific: Classifier | None
