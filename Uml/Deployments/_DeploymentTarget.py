from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._NamedElement import NamedElement

class DeploymentTarget(NamedElement):
    """UML metaclass DeploymentTarget."""
    __spec__ = SPECIFICATIONS['DeploymentTarget']
    deployedElement: list[PackageableElement]
    deployment: list[Deployment]
