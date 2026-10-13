from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._NamedElement import NamedElement

class Namespace(NamedElement):
    """UML metaclass Namespace."""
    __spec__ = SPECIFICATIONS['Namespace']
    elementImport: list[ElementImport]
    importedMember: list[PackageableElement]
    member: list[NamedElement]
    ownedMember: list[NamedElement]
    ownedRule: list[Constraint]
    packageImport: list[PackageImport]
    def excludeCollisions(self, *args, **kwargs):
        try:
            return _operation(self, 'Namespace', 'excludeCollisions', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def getNamesOfMember(self, *args, **kwargs):
        try:
            return _operation(self, 'Namespace', 'getNamesOfMember', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def importMembers(self, *args, **kwargs):
        try:
            return _operation(self, 'Namespace', 'importMembers', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def membersAreDistinguishable(self, *args, **kwargs):
        try:
            return _operation(self, 'Namespace', 'membersAreDistinguishable', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
