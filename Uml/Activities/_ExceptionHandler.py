from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._Element import Element

class ExceptionHandler(Element):
    """UML metaclass ExceptionHandler."""
    __spec__ = SPECIFICATIONS['ExceptionHandler']
    exceptionInput: ObjectNode | None
    exceptionType: list[Classifier]
    handlerBody: ExecutableNode | None
    protectedNode: ExecutableNode | None
