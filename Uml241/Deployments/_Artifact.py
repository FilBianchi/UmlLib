from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Classification._Classifier import Classifier
from ..Deployments._DeployedArtifact import DeployedArtifact

class Artifact(Classifier, DeployedArtifact):
    """UML metaclass Artifact."""
    __spec__ = SPECIFICATIONS['Artifact']
    fileName: str | None
    manifestation: list[Manifestation]
    nestedArtifact: list[Artifact]
    ownedAttribute: list[Property]
    ownedOperation: list[Operation]
