from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._DirectedRelationship import DirectedRelationship

class Generalization(DirectedRelationship):
    """UML metaclass Generalization."""
    __spec__ = SPECIFICATIONS['Generalization']
    general: Classifier | None
    generalizationSet: list[GeneralizationSet]
    isSubstitutable: bool | None
    specific: Classifier | None
