from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._TypedElement import TypedElement
from ..CommonStructure._ParameterableElement import ParameterableElement

class ConnectableElement(TypedElement, ParameterableElement):
    """UML metaclass ConnectableElement."""
    __spec__ = SPECIFICATIONS['ConnectableElement']
    end: list[ConnectorEnd]
    templateParameter: ConnectableElementTemplateParameter | None
