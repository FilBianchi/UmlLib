from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._DirectedRelationship import DirectedRelationship

class TemplateBinding(DirectedRelationship):
    """UML metaclass TemplateBinding."""
    __spec__ = SPECIFICATIONS['TemplateBinding']
    boundElement: TemplateableElement | None
    parameterSubstitution: list[TemplateParameterSubstitution]
    signature: TemplateSignature | None
