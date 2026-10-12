"""Behavior context and parameter queries translated directly into Python."""
from . import query, invariant, kind


@query('Behavior.behavioredClassifier')
def behaviored_classifier(self, **variables):
    current = variables['from']
    while current is not None:
        if kind(self, current, 'BehavioredClassifier'): return current
        current = current.owner
    return None


@query('Behavior.context')
def context(self):
    owner = self.owner
    if owner is None: return None
    if kind(self, owner, 'Class') and self in owner.nestedClassifier: return None
    classifier = self.behavioredClassifier(owner)
    if kind(self, classifier, 'Behavior') and classifier.context is not None: return classifier.context
    return classifier


@query('Behavior.inputParameters')
def input_parameters(self): return [parameter for parameter in self.ownedParameter if parameter.direction.value in ('in', 'inout')]


@query('Behavior.outputParameters')
def output_parameters(self): return [parameter for parameter in self.ownedParameter if parameter.direction.value in ('out', 'inout', 'return')]


@invariant('Behavior.parameters_match')
def matching_parameters(self): return self.specification is None or len(self.ownedParameter) == len(self.specification.ownedParameter)


@invariant('Behavior.most_one_behavior')
def one_method(self):
    if self.specification is None: return True
    if self.context is None: raise ValueError('Method has no context classifier')
    return sum(behavior.specification is self.specification for behavior in self.context.ownedBehavior) == 1


@invariant('Behavior.feature_of_context_classifier')
def context_feature(self):
    if self.specification is None: return True
    if self.context is None: raise ValueError('Behavior has no context classifier')
    return self.specification in self.context.feature
