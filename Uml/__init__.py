"""UML 2.5.1 organized by its specification packages."""
from ._classes import *
from . import Activities, Values, UseCases, StructuredClassifiers, StateMachines, SimpleClassifiers, Packages, Interactions, InformationFlows, Deployments, CommonStructure, CommonBehavior, Classification, Actions

# Convenient singular alias; StateMachines is the OMG package name.
StateMachine = StateMachines
