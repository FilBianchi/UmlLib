from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation

class InteractionOperatorKind(Enum):
    seq = 'seq'
    alt = 'alt'
    opt = 'opt'
    break_ = 'break'
    par = 'par'
    strict = 'strict'
    loop = 'loop'
    critical = 'critical'
    neg = 'neg'
    assert_ = 'assert'
    ignore = 'ignore'
    consider = 'consider'
