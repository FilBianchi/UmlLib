from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Classification._RedefinableElement import RedefinableElement

class ExtensionPoint(RedefinableElement):
    """UML metaclass ExtensionPoint."""
    __spec__ = SPECIFICATIONS['ExtensionPoint']
    useCase: UseCase | None
