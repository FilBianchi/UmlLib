from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation

class PseudostateKind(Enum):
    initial = 'initial'
    deepHistory = 'deepHistory'
    shallowHistory = 'shallowHistory'
    join = 'join'
    fork = 'fork'
    junction = 'junction'
    choice = 'choice'
    entryPoint = 'entryPoint'
    exitPoint = 'exitPoint'
    terminate = 'terminate'
