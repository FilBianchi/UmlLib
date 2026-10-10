from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._TemplateParameter import TemplateParameter

class ClassifierTemplateParameter(TemplateParameter):
    """UML metaclass ClassifierTemplateParameter."""
    __spec__ = SPECIFICATIONS['ClassifierTemplateParameter']
    allowSubstitutable: bool | None
    constrainingClassifier: list[Classifier]
    parameteredElement: Classifier | None
