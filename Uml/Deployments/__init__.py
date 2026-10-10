"""UML 2.5.1 Deployments package."""
from importlib import import_module

__all__ = ['Artifact', 'CommunicationPath', 'DeployedArtifact', 'Deployment', 'DeploymentSpecification', 'DeploymentTarget', 'Device', 'ExecutionEnvironment', 'Manifestation', 'Node']

def __getattr__(name):
    if name not in __all__: raise AttributeError(name)
    value = getattr(import_module("._" + name, __name__), name)
    globals()[name] = value
    return value
