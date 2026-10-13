from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._Element import Element

class TemplateSignature(Element):
    """UML metaclass TemplateSignature."""
    __spec__ = SPECIFICATIONS['TemplateSignature']
    ownedParameter: list[TemplateParameter]
    parameter: list[TemplateParameter]
    template: TemplateableElement | None
