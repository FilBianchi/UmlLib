from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Deployments._DeploymentTarget import DeploymentTarget
from ..CommonStructure._PackageableElement import PackageableElement
from ..Deployments._DeployedArtifact import DeployedArtifact

class InstanceSpecification(DeploymentTarget, PackageableElement, DeployedArtifact):
    """UML metaclass InstanceSpecification."""
    __spec__ = SPECIFICATIONS['InstanceSpecification']
    classifier: list[Classifier]
    slot: list[Slot]
    specification: ValueSpecification | None
