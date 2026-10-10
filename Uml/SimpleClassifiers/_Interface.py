from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Classification._Classifier import Classifier

class Interface(Classifier):
    """UML metaclass Interface."""
    __spec__ = SPECIFICATIONS['Interface']
    nestedClassifier: list[Classifier]
    ownedAttribute: list[Property]
    ownedOperation: list[Operation]
    ownedReception: list[Reception]
    protocol: ProtocolStateMachine | None
    redefinedInterface: list[Interface]
