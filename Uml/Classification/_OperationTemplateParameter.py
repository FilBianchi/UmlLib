from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._TemplateParameter import TemplateParameter

class OperationTemplateParameter(TemplateParameter):
    """UML metaclass OperationTemplateParameter."""
    __spec__ = SPECIFICATIONS['OperationTemplateParameter']
    parameteredElement: Operation | None
