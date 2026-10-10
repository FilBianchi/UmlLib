from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Classification._InstanceSpecification import InstanceSpecification

class EnumerationLiteral(InstanceSpecification):
    """UML metaclass EnumerationLiteral."""
    __spec__ = SPECIFICATIONS['EnumerationLiteral']
    classifier: Enumeration | None
    enumeration: Enumeration | None
