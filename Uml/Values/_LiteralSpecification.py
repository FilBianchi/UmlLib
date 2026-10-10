from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Values._ValueSpecification import ValueSpecification

class LiteralSpecification(ValueSpecification):
    """UML metaclass LiteralSpecification."""
    __spec__ = SPECIFICATIONS['LiteralSpecification']
