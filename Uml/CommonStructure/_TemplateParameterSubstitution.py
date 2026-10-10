from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._Element import Element

class TemplateParameterSubstitution(Element):
    """UML metaclass TemplateParameterSubstitution."""
    __spec__ = SPECIFICATIONS['TemplateParameterSubstitution']
    actual: ParameterableElement | None
    formal: TemplateParameter | None
    ownedActual: ParameterableElement | None
    templateBinding: TemplateBinding | None
