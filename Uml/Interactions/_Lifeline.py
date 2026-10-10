from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._NamedElement import NamedElement

class Lifeline(NamedElement):
    """UML metaclass Lifeline."""
    __spec__ = SPECIFICATIONS['Lifeline']
    coveredBy: list[InteractionFragment]
    decomposedAs: PartDecomposition | None
    interaction: Interaction | None
    represents: ConnectableElement | None
    selector: ValueSpecification | None
