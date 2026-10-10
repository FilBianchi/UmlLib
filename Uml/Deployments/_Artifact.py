from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
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
