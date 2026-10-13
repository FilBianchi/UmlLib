from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation

class AggregationKind(Enum):
    none = 'none'
    shared = 'shared'
    composite = 'composite'
