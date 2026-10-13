from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._TemplateParameter import TemplateParameter

class OperationTemplateParameter(TemplateParameter):
    """UML metaclass OperationTemplateParameter."""
    __spec__ = SPECIFICATIONS['OperationTemplateParameter']
    parameteredElement: Operation | None
