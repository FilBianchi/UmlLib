from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._Element import Element

class TemplateSignature(Element):
    """UML metaclass TemplateSignature."""
    __spec__ = SPECIFICATIONS['TemplateSignature']
    ownedParameter: list[TemplateParameter]
    parameter: list[TemplateParameter]
    template: TemplateableElement | None
