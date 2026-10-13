from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._TypedElement import TypedElement
from ..CommonStructure._ParameterableElement import ParameterableElement

class ConnectableElement(TypedElement, ParameterableElement):
    """UML metaclass ConnectableElement."""
    __spec__ = SPECIFICATIONS['ConnectableElement']
    end: list[ConnectorEnd]
    templateParameter: ConnectableElementTemplateParameter | None
