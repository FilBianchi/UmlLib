from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._Element import Element

class QualifierValue(Element):
    """UML metaclass QualifierValue."""
    __spec__ = SPECIFICATIONS['QualifierValue']
    qualifier: Property | None
    value: InputPin | None
