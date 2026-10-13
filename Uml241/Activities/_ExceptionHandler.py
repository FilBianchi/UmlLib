from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._Element import Element

class ExceptionHandler(Element):
    """UML metaclass ExceptionHandler."""
    __spec__ = SPECIFICATIONS['ExceptionHandler']
    exceptionInput: ObjectNode | None
    exceptionType: list[Classifier]
    handlerBody: ExecutableNode | None
    protectedNode: ExecutableNode | None
