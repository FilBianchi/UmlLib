from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._Element import Element

class TemplateParameter(Element):
    """UML metaclass TemplateParameter."""
    __spec__ = SPECIFICATIONS['TemplateParameter']
    default: ParameterableElement | None
    ownedDefault: ParameterableElement | None
    ownedParameteredElement: ParameterableElement | None
    parameteredElement: ParameterableElement | None
    signature: TemplateSignature | None
