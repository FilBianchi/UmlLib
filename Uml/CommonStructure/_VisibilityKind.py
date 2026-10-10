from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented

class VisibilityKind(Enum):
    public = 'public'
    private = 'private'
    protected = 'protected'
    package = 'package'
