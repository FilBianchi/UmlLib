from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented

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
