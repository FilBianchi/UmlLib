"""Activity graph constraints including paths through intervening control nodes."""
from . import invariant, kind, instances
from .constraints_basic import predicates, required, enum
from .constraints_actions import pins_match, conforms


def homogeneous(self):
    edges = list(self.incoming) + list(self.outgoing)
    return all(kind(self, e, 'ControlFlow') for e in edges) or all(kind(self, e, 'ObjectFlow') for e in edges)


predicates({
    'Activity.maximum_one_parameter_node': lambda s: all(sum(kind(s, n, 'ActivityParameterNode') and n.parameter is p for n in s.node) == 1 for p in s.ownedParameter if enum(p.direction) != 'inout'),
    'ActivityEdge.source_and_target': lambda s: s.activity is None or required(s.source).containingActivity() is s.activity and required(s.target).containingActivity() is s.activity,
    'ActivityGroup.nodes_and_edges': lambda s: all(n.activity is s.containingActivity() for n in s.containedNode) and all(e.activity is s.containingActivity() for e in s.containedEdge),
    'ActivityParameterNode.no_outgoing_edges': lambda s: not s.incoming or bool(s.outgoing) or enum(required(s.parameter).direction) in ('out', 'inout', 'return'),
    'ActivityParameterNode.has_parameters': lambda s: s.parameter in required(s.activity).ownedParameter,
    'ActivityParameterNode.same_type': lambda s: s.type is required(s.parameter).type,
    'ActivityParameterNode.no_incoming_edges': lambda s: not s.outgoing or bool(s.incoming) or enum(required(s.parameter).direction) in ('in', 'inout'),
    'ActivityParameterNode.no_edges': lambda s: not s.incoming or not s.outgoing,
    'ActivityPartition.represents_property_and_is_contained': lambda s: not kind(s, s.represents, 'Property') or s.superPartition is None or kind(s, s.superPartition.represents, 'Classifier') and s.represents.owner is s.superPartition.represents or kind(s, s.superPartition.represents, 'Property') and s.represents.owner is s.superPartition.represents.type,
    'ActivityPartition.represents_property': lambda s: not kind(s, s.represents, 'Property') or s.superPartition is None or not kind(s, s.superPartition.represents, 'Classifier') or all(kind(s, p.represents, 'Property') and p.represents.owner is s.superPartition.represents for p in s.superPartition.subpartition if not p.isExternal),
    'ActivityPartition.dimension_not_contained': lambda s: not s.isDimension or s.superPartition is None,
    'ControlFlow.object_nodes': lambda s: all(not kind(s, n, 'ObjectNode') or n.isControlType for n in (s.source, s.target)),
    'DecisionNode.zero_input_parameters': lambda s: s.decisionInput is None or s.decisionInputFlow is not None or not any(kind(s, e, 'ControlFlow') for e in s.incoming) or not s.decisionInput.inputParameters(),
    'DecisionNode.decision_input_flow_incoming': lambda s: s.decisionInputFlow is None or s.decisionInputFlow in s.incoming,
    'DecisionNode.two_input_parameters': lambda s: s.decisionInput is None or s.decisionInputFlow is None or not all(kind(s, e, 'ObjectFlow') for e in s.incoming) or len(s.decisionInput.inputParameters()) == 2,
    'DecisionNode.incoming_outgoing_edges': lambda s: len(s.incoming) in (1, 2) and bool(s.outgoing),
    'DecisionNode.incoming_control_one_input_parameter': lambda s: s.decisionInput is None or s.decisionInputFlow is None or not any(kind(s, e, 'ControlFlow') for e in s.incoming) or len(s.decisionInput.inputParameters()) == 1,
    'DecisionNode.parameters': lambda s: s.decisionInput is None or all(enum(p.direction) not in ('out', 'inout') for p in s.decisionInput.ownedParameter) and sum(enum(p.direction) == 'return' for p in s.decisionInput.ownedParameter) == 1,
    'DecisionNode.incoming_object_one_input_parameter': lambda s: s.decisionInput is None or s.decisionInputFlow is not None or not all(kind(s, e, 'ObjectFlow') for e in s.incoming) or len(s.decisionInput.inputParameters()) == 1,
    'ExceptionHandler.handler_body_edges': lambda s: not required(s.handlerBody).incoming and not s.handlerBody.outgoing and not required(s.exceptionInput).incoming,
    'ExceptionHandler.output_pins': lambda s: not kind(s, s.protectedNode, 'Action') or not s.protectedNode.output or kind(s, s.handlerBody, 'Action') and pins_match(s.handlerBody.output, s.protectedNode.output),
    'ExceptionHandler.one_input': lambda s: kind(s, s.handlerBody, 'Action') and list(s.handlerBody.input) == [required(s.exceptionInput)],
    'ExceptionHandler.edge_source_target': lambda s: all(e.target in required(s.handlerBody).allOwnedNodes() for n in s.handlerBody.allOwnedNodes() for e in n.outgoing) and all(e.source in s.handlerBody.allOwnedNodes() for n in s.handlerBody.allOwnedNodes() for e in n.incoming),
    'ExceptionHandler.handler_body_owner': lambda s: required(s.handlerBody).owner is required(s.protectedNode).owner,
    'ExceptionHandler.exception_input_type': lambda s: required(s.exceptionInput).type is None or all(conforms(t, s.exceptionInput.type) for t in s.exceptionType),
    'FinalNode.no_outgoing_edges': lambda s: not s.outgoing,
    'ForkNode.edges': homogeneous,
    'ForkNode.one_incoming_edge': lambda s: len(s.incoming) == 1,
    'InitialNode.no_incoming_edges': lambda s: not s.incoming,
    'InitialNode.control_edges': lambda s: all(kind(s, e, 'ControlFlow') for e in s.outgoing),
    'InterruptibleActivityRegion.interrupting_edges': lambda s: all(e.source in s.node and e.target not in s.node and required(e.target).containingActivity() is s.inActivity for e in s.interruptingEdge),
    'JoinNode.one_outgoing_edge': lambda s: len(s.outgoing) == 1,
    'JoinNode.incoming_object_flow': lambda s: all(kind(s, e, 'ObjectFlow' if any(kind(s, i, 'ObjectFlow') for i in s.incoming) else 'ControlFlow') for e in s.outgoing),
    'MergeNode.one_outgoing_edge': lambda s: len(s.outgoing) == 1,
    'MergeNode.edges': homogeneous,
    'ObjectFlow.input_and_output_parameter': lambda s: s.selection is None or len(s.selection.inputParameters()) == 1 and all(not p.isUnique and p.is_(0, float('inf')) for p in s.selection.inputParameters()) and len(s.selection.outputParameters()) == 1,
    'ObjectFlow.no_executable_nodes': lambda s: not kind(s, s.source, 'ExecutableNode') and not kind(s, s.target, 'ExecutableNode'),
    'ObjectFlow.transformation_behavior': lambda s: s.transformation is None or len(s.transformation.inputParameters()) == len(s.transformation.outputParameters()) == 1,
    'ObjectFlow.selection_behavior': lambda s: s.selection is None or kind(s, s.source, 'ObjectNode'),
    'ObjectFlow.is_multicast_or_is_multireceive': lambda s: not (s.isMulticast and s.isMultireceive),
    'ObjectNode.input_output_parameter': lambda s: s.selection is None or len(s.selection.inputParameters()) == 1 and all(not p.isUnique and p.is_(0, float('inf')) and conforms(s.type, p.type) for p in s.selection.inputParameters()) and len(s.selection.outputParameters()) == 1 and all(conforms(s.type, p.type) for p in s.selection.outputParameters()),
    'ObjectNode.selection_behavior': lambda s: (s.selection is not None) == (enum(s.ordering) == 'ordered'),
    'ObjectNode.object_flow_edges': lambda s: s.isControlType or all(kind(s, e, 'ObjectFlow') for e in list(s.incoming) + list(s.outgoing)),
})


@invariant('Activity.maximum_two_parameter_nodes')
def inout_nodes(self):
    for parameter in self.ownedParameter:
        if enum(parameter.direction) != 'inout': continue
        nodes = [n for n in self.node if kind(self, n, 'ActivityParameterNode') and n.parameter is parameter]
        if len(nodes) != 2 or sum(bool(n.incoming) for n in nodes) > 1 or sum(bool(n.outgoing) for n in nodes) > 1: return False
    return True


@invariant('DecisionNode.edges')
def decision_edges(self):
    edges = [e for e in list(self.incoming) + list(self.outgoing) if e is not self.decisionInputFlow]
    return all(kind(self, e, 'ControlFlow') for e in edges) or all(kind(self, e, 'ObjectFlow') for e in edges)


@invariant('ActivityGroup.not_contained')
def groups_disjoint(self):
    groups, pending = set(), list(self.subgroup) + ([] if self.superGroup is None else [self.superGroup])
    while pending:
        group = pending.pop()
        if group is self: return False
        if group in groups: continue
        groups.add(group)
        if group is self.superGroup or self in group.subgroup:
            if group.superGroup is not None: pending.append(group.superGroup)
        else: pending.extend(group.subgroup)
    return all(not set(g.containedNode) & set(self.containedNode) and not set(g.containedEdge) & set(self.containedEdge) for g in groups)


@invariant('ActivityPartition.represents_classifier')
def represented_classifier(self):
    if self.isExternal or not kind(self, self.represents, 'Classifier') or self.superPartition is None: return True
    child, parent = self.represents, self.superPartition.represents
    if not kind(self, parent, 'Classifier'): return False
    return (kind(self, parent, 'BehavioredClassifier') and kind(self, child, 'Behavior') and child in parent.ownedBehavior or kind(self, parent, 'Class') and child in parent.nestedClassifier or any(a.type is child and a.isComposite and b is not a and b.type is parent for assoc in instances(self, 'Association') for a in assoc.memberEnd for b in assoc.memberEnd))


def endpoints(self, upstream):
    result, seen = [], set()
    pending = [required(self.source if upstream else self.target)]
    while pending:
        node = pending.pop()
        if node in seen: continue
        seen.add(node)
        if kind(self, node, 'ObjectNode'): result.append(node)
        elif kind(self, node, 'ControlNode'):
            pending.extend(required(e.source if upstream else e.target) for e in (node.incoming if upstream else node.outgoing) if kind(self, e, 'ObjectFlow'))
    return result


@invariant('ObjectFlow.compatible_types')
def flow_types(self):
    if self.transformation is not None: return True
    return all(a.type is None or b.type is None or conforms(a.type, b.type) for a in endpoints(self, True) for b in endpoints(self, False))


@invariant('ObjectFlow.same_upper_bounds')
def flow_bounds(self):
    return all(required(a.upperBound).unlimitedValue() == required(b.upperBound).unlimitedValue() for a in endpoints(self, True) for b in endpoints(self, False))


@invariant('ObjectFlow.target')
def flow_weight(self):
    if self.weight is None: return True
    weight = self.weight.integerValue()
    if weight is None: return True  # A nonconstant weight is outside this conditional rule.
    return all(required(n.upperBound).unlimitedValue() >= weight for n in endpoints(self, False))
