from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._Dependency import Dependency

class Deployment(Dependency):
    """UML metaclass Deployment."""
    __spec__ = SPECIFICATIONS['Deployment']
    configuration: list[DeploymentSpecification]
    deployedArtifact: list[DeployedArtifact]
    location: DeploymentTarget | None
