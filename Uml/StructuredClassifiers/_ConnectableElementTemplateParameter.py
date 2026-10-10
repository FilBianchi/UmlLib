from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._TemplateParameter import TemplateParameter

class ConnectableElementTemplateParameter(TemplateParameter):
    """UML metaclass ConnectableElementTemplateParameter."""
    __spec__ = SPECIFICATIONS['ConnectableElementTemplateParameter']
    parameteredElement: ConnectableElement | None
