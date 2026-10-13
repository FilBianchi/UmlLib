from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Classification._RedefinableElement import RedefinableElement

class ExtensionPoint(RedefinableElement):
    """UML metaclass ExtensionPoint."""
    __spec__ = SPECIFICATIONS['ExtensionPoint']
    useCase: UseCase | None
