from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Classification._InstanceSpecification import InstanceSpecification

class EnumerationLiteral(InstanceSpecification):
    """UML metaclass EnumerationLiteral."""
    __spec__ = SPECIFICATIONS['EnumerationLiteral']
    classifier: Enumeration | None
    enumeration: Enumeration | None
