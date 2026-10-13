from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Classification._Classifier import Classifier

class StructuredClassifier(Classifier):
    """UML metaclass StructuredClassifier."""
    __spec__ = SPECIFICATIONS['StructuredClassifier']
    ownedAttribute: list[Property]
    ownedConnector: list[Connector]
    part: list[Property]
    role: list[ConnectableElement]
