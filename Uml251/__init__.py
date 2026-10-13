"""Explicit UML 2.5.1 namespace; Uml and UML remain compatible aliases."""
from Uml import *
from Uml._classes import __all__
from Uml import Activities,Actions,Classification,CommonBehavior,CommonStructure,Deployments,InformationFlows,Interactions,Packages,SimpleClassifiers,StateMachines,StructuredClassifiers,UseCases,Values
from umltools import ModelSession,UnsupportedSemanticsError,DeletedElementError,DeletionRestrictedError

SEMANTIC_VERSION='2.5.1'
StateMachine=StateMachines
