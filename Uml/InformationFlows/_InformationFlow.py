from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._DirectedRelationship import DirectedRelationship
from ..CommonStructure._PackageableElement import PackageableElement

class InformationFlow(DirectedRelationship, PackageableElement):
    """UML metaclass InformationFlow."""
    __spec__ = SPECIFICATIONS['InformationFlow']
    conveyed: list[Classifier]
    informationSource: list[NamedElement]
    informationTarget: list[NamedElement]
    realization: list[Relationship]
    realizingActivityEdge: list[ActivityEdge]
    realizingConnector: list[Connector]
    realizingMessage: list[Message]
