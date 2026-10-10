from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._Element import Element

class TemplateParameter(Element):
    """UML metaclass TemplateParameter."""
    __spec__ = SPECIFICATIONS['TemplateParameter']
    default: ParameterableElement | None
    ownedDefault: ParameterableElement | None
    ownedParameteredElement: ParameterableElement | None
    parameteredElement: ParameterableElement | None
    signature: TemplateSignature | None
