from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented

class ParameterDirectionKind(Enum):
    in_ = 'in'
    inout = 'inout'
    out = 'out'
    return_ = 'return'
