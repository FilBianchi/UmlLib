from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._Dependency import Dependency

class Deployment(Dependency):
    """UML metaclass Deployment."""
    __spec__ = SPECIFICATIONS['Deployment']
    configuration: list[DeploymentSpecification]
    deployedArtifact: list[DeployedArtifact]
    location: DeploymentTarget | None
