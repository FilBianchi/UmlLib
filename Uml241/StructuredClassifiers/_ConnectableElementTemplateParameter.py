from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._TemplateParameter import TemplateParameter

class ConnectableElementTemplateParameter(TemplateParameter):
    """UML metaclass ConnectableElementTemplateParameter."""
    __spec__ = SPECIFICATIONS['ConnectableElementTemplateParameter']
    parameteredElement: ConnectableElement | None
