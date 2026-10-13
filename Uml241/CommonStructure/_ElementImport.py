from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._DirectedRelationship import DirectedRelationship

class ElementImport(DirectedRelationship):
    """UML metaclass ElementImport."""
    __spec__ = SPECIFICATIONS['ElementImport']
    alias: str | None
    importedElement: PackageableElement | None
    importingNamespace: Namespace | None
    visibility: VisibilityKind | None
    def getName(self, *args, **kwargs):
        try:
            return _operation(self, 'ElementImport', 'getName', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
