from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
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
