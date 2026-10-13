from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._Element import Element

class TemplateParameterSubstitution(Element):
    """UML metaclass TemplateParameterSubstitution."""
    __spec__ = SPECIFICATIONS['TemplateParameterSubstitution']
    actual: ParameterableElement | None
    formal: TemplateParameter | None
    ownedActual: ParameterableElement | None
    templateBinding: TemplateBinding | None
