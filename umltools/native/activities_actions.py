"""Activity and action queries, translated from their UML body conditions."""
from . import query, kind, unique, instances, NativeNotImplemented


@query('ActivityEdge.isConsistentWith', 'ActivityNode.isConsistentWith')
def consistent_node(self, redefiningElement):
    expected = 'ActivityEdge' if kind(self, self, 'ActivityEdge') else 'ActivityNode'
    return kind(self, redefiningElement, expected)


@query('ActivityGroup.containingActivity')
def group_activity(self):
    return self.superGroup.containingActivity() if self.superGroup is not None else self.inActivity


@query('ActivityNode.containingActivity', 'StructuredActivityNode.containingActivity')
def node_activity(self):
    return self.inStructuredNode.containingActivity() if self.inStructuredNode is not None else self.activity


@query('Variable.isAccessibleBy')
def accessible(self, a):
    return a in self.scope.allOwnedNodes() if self.scope is not None else a.containingActivity() is self.activityScope


@query('Action.allActions', 'ConditionalNode.allActions', 'LoopNode.allActions')
def single_action(self): return [self]


@query('Action.allOwnedNodes')
def action_nodes(self): return unique(list(self.input) + list(self.output))


@query('Action.containingBehavior')
def containing_behavior(self):
    if self.inStructuredNode is not None: return self.inStructuredNode.containingBehavior()
    if self.activity is not None: return self.activity
    # Interaction::action is an association-owned, non-navigable end.
    return next((interaction for interaction in instances(self, 'Interaction') if self in interaction.action), None)


@query('Action.context')
def action_context(self):
    behavior = self.containingBehavior()
    return None if behavior is None else behavior.context or behavior


@query('CallAction.inputParameters', 'CallAction.outputParameters')
def abstract_parameters(self):
    raise NativeNotImplemented('Abstract CallAction query requires a concrete overriding operation')


@query('CallBehaviorAction.inputParameters')
def behavior_inputs(self):
    if self.behavior is None: raise ValueError('CallBehaviorAction requires a behavior')
    return self.behavior.inputParameters()


@query('CallBehaviorAction.outputParameters')
def behavior_outputs(self):
    if self.behavior is None: raise ValueError('CallBehaviorAction requires a behavior')
    return self.behavior.outputParameters()


@query('CallOperationAction.inputParameters')
def operation_inputs(self):
    if self.operation is None: raise ValueError('CallOperationAction requires an operation')
    return self.operation.inputParameters()


@query('CallOperationAction.outputParameters')
def operation_outputs(self):
    if self.operation is None: raise ValueError('CallOperationAction requires an operation')
    return self.operation.outputParameters()


@query('StructuredActivityNode.allActions')
def structured_actions(self):
    return unique([a for node in self.node if kind(self, node, 'Action') for a in node.allActions()] + [self])


@query('StructuredActivityNode.allOwnedNodes')
def structured_nodes(self):
    return unique(action_nodes(self) + list(self.node) + [n for node in self.node if kind(self, node, 'Action') for n in node.allOwnedNodes()])


@query('StructuredActivityNode.sourceNodes')
def source_nodes(self):
    return unique(list(self.node) + list(self.input) + [p for node in self.node if kind(self, node, 'Action') for p in node.output])


@query('StructuredActivityNode.targetNodes')
def target_nodes(self):
    return unique(list(self.node) + list(self.output) + [p for node in self.node if kind(self, node, 'Action') for p in node.input])


@query('LoopNode.sourceNodes')
def loop_sources(self): return unique(source_nodes(self) + list(self.loopVariable))


@query('LinkAction.association')
def link_association(self):
    if not self.endData or self.endData[0].end is None: raise ValueError('LinkAction requires end data with an end')
    return self.endData[0].end.association


@query('LinkEndData.allPins')
def link_pins(self):
    return ([] if self.value is None else [self.value]) + [q.value for q in self.qualifier if q.value is not None]


@query('LinkEndCreationData.allPins')
def creation_pins(self): return link_pins(self) + ([] if self.insertAt is None else [self.insertAt])


@query('LinkEndDestructionData.allPins')
def destruction_pins(self): return link_pins(self) + ([] if self.destroyAt is None else [self.destroyAt])


@query('ReadLinkAction.openEnd')
def open_ends(self): return unique(data.end for data in self.endData if data.value is None and data.end is not None)


@query('StartObjectBehaviorAction.behavior')
def object_behavior(self):
    if self.object is None: raise ValueError('StartObjectBehaviorAction requires an object pin')
    type_ = self.object.type
    if kind(self, type_, 'Behavior'): return type_
    if kind(self, type_, 'BehavioredClassifier'): return type_.classifierBehavior
    return None


@query('StartObjectBehaviorAction.inputParameters')
def object_inputs(self):
    behavior = self.behavior()
    if behavior is None: raise ValueError('Object has no callable behavior')
    return behavior.inputParameters()


@query('StartObjectBehaviorAction.outputParameters')
def object_outputs(self):
    behavior = self.behavior()
    if behavior is None: raise ValueError('Object has no callable behavior')
    return behavior.outputParameters()
