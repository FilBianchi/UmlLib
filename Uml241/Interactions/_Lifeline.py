from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._NamedElement import NamedElement

class Lifeline(NamedElement):
    """UML metaclass Lifeline."""
    __spec__ = SPECIFICATIONS['Lifeline']
    coveredBy: list[InteractionFragment]
    decomposedAs: PartDecomposition | None
    interaction: Interaction | None
    represents: ConnectableElement | None
    selector: ValueSpecification | None
