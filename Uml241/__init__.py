"""UML 2.4.1 declarations; groups are convenience API namespaces."""
from ._classes import *
from . import CommonStructure, Actions, Interactions, Activities, UseCases, CommonBehavior, Deployments, StructuredClassifiers, Classification, SimpleClassifiers, StateMachines, Values, Packages, InformationFlows

# Convenient singular alias; StateMachines is the OMG package name.
StateMachine = StateMachines

from ._runtime import engine as _engine
ModelSession = _engine.ModelSession
UnsupportedSemanticsError = _engine.UnsupportedSemanticsError
DeletedElementError = _engine.DeletedElementError
DeletionRestrictedError = _engine.DeletionRestrictedError
SEMANTIC_VERSION = "2.4.1"
