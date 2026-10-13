from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._NamedElement import NamedElement

class DeploymentTarget(NamedElement):
    """UML metaclass DeploymentTarget."""
    __spec__ = SPECIFICATIONS['DeploymentTarget']
    deployedElement: list[PackageableElement]
    deployment: list[Deployment]
