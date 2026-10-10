from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented

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
