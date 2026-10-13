from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._DirectedRelationship import DirectedRelationship

class TemplateBinding(DirectedRelationship):
    """UML metaclass TemplateBinding."""
    __spec__ = SPECIFICATIONS['TemplateBinding']
    boundElement: TemplateableElement | None
    parameterSubstitution: list[TemplateParameterSubstitution]
    signature: TemplateSignature | None
