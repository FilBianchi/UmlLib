"""Action well-formedness predicates, with explicit pin and signature checks."""
from collections import Counter
from . import invariant, kind, reverse, single
from .constraints_basic import predicates, required, enum
from .values import upper_bound


def primitive(value, name):
    return value is not None and kind(value, value, 'PrimitiveType') and value.name == name


def one(pin): return required(pin).is_(1, 1)
def conforms(a, b): return required(a).conformsTo(required(b))
def pin_matches(a, b, unique=False):
    return conforms(a.type, b.type) and a.isOrdered == b.isOrdered and (not unique or a.isUnique == b.isUnique) and a.compatibleWith(b)


def pins_match(a, b, unique=False):
    return len(a) == len(b) and all(pin_matches(x, y, unique) for x, y in zip(a, b))


def outputs(nodes): return [p for n in nodes for a in required(n).allActions() for p in a.output]
def index_pin(pin): return pin is not None and primitive(pin.type, 'UnlimitedNatural') and one(pin)


predicates({
    'ValueSpecificationAction.multiplicity': lambda s: one(s.result),
    'ValueSpecificationAction.compatible_type': lambda s: conforms(required(s.value).type, required(s.result).type),
    'VariableAction.scope_of_variable': lambda s: required(s.variable).isAccessibleBy(s),
    'WriteStructuralFeatureAction.multiplicity_of_result': lambda s: s.result is None or one(s.result),
    'WriteStructuralFeatureAction.type_of_value': lambda s: s.value is None or conforms(s.value.type, required(s.structuralFeature).type),
    'WriteStructuralFeatureAction.multiplicity_of_value': lambda s: s.value is None or one(s.value),
    'WriteStructuralFeatureAction.type_of_result': lambda s: s.result is None or s.result.type is required(s.object).type,
    'WriteVariableAction.value_type': lambda s: s.value is None or conforms(s.value.type, required(s.variable).type),
    'WriteVariableAction.multiplicity': lambda s: s.value is None or one(s.value),
    'AcceptCallAction.trigger_call_event': lambda s: len(s.trigger) == 1 and kind(s, s.trigger[0].event, 'CallEvent'),
    'AcceptCallAction.unmarshall': lambda s: s.isUnmarshall is True,
    'AcceptCallAction.result_pins': lambda s: pins_match(required(s.trigger[0].event).operation.inputParameters(), s.result),
    'AcceptEventAction.one_output_pin': lambda s: s.isUnmarshall or not any(kind(s, t.event, 'SignalEvent') or kind(s, t.event, 'TimeEvent') for t in s.trigger) or len(s.output) == 1 and one(s.output[0]),
    'AcceptEventAction.no_input_pins': lambda s: not s.input,
    'AcceptEventAction.no_output_pins': lambda s: type(s) is not s.__registry__['AcceptEventAction'] or not all(kind(s, t.event, 'ChangeEvent') or kind(s, t.event, 'CallEvent') for t in s.trigger) or not s.output,
    'ActionInputPin.input_pin': lambda s: all(kind(s, p, 'ActionInputPin') for p in required(s.fromAction).input),
    'ActionInputPin.one_output_pin': lambda s: len(required(s.fromAction).output) == 1,
    'ActionInputPin.no_control_or_object_flow': lambda s: not required(s.fromAction).incoming and not s.fromAction.outgoing and all(not p.incoming for p in s.fromAction.input) and all(not p.outgoing for p in s.fromAction.output),
    'AddStructuralFeatureValueAction.required_value': lambda s: s.value is not None,
    'AddVariableValueAction.required_value': lambda s: s.value is not None,
    'BroadcastSignalAction.number_of_arguments': lambda s: len(s.argument) == len(required(s.signal).allAttributes()),
    'BroadcastSignalAction.type_ordering_multiplicity': lambda s: pins_match(s.argument, required(s.signal).allAttributes()),
    'BroadcastSignalAction.no_onport': lambda s: s.onPort is None,
    'CallAction.argument_pins': lambda s: pins_match(s.argument, s.inputParameters()),
    'CallAction.result_pins': lambda s: pins_match(s.outputParameters(), s.result),
    'CallAction.synchronous_call': lambda s: not s.result or s.isSynchronous,
    'CallBehaviorAction.no_onport': lambda s: s.onPort is None,
    'Clause.body_output_pins': lambda s: set(s.bodyOutput) <= set(outputs(s.body)),
    'Clause.decider_output': lambda s: s.decider in outputs(s.test) and primitive(s.decider.type, 'Boolean') and one(s.decider),
    'Clause.test_and_body': lambda s: not set(s.test) & set(s.body),
    'ClearAssociationAction.multiplicity': lambda s: one(s.object),
    'ClearAssociationAction.same_type': lambda s: any(conforms(required(s.object).type, e.type) for e in required(s.association).memberEnd),
    'ClearStructuralFeatureAction.type_of_result': lambda s: s.result is None or s.result.type is required(s.object).type,
    'ClearStructuralFeatureAction.multiplicity_of_result': lambda s: s.result is None or one(s.result),
    'ConditionalNode.result_no_incoming': lambda s: all(not p.incoming for p in s.result),
    'ConditionalNode.no_input_pins': lambda s: not s.input,
    'ConditionalNode.one_clause_with_executable_node': lambda s: all(sum(n in c.test or n in c.body for c in s.clause) == 1 for n in s.node if kind(s, n, 'ExecutableNode')),
    'ConditionalNode.matching_output_pins': lambda s: all(pins_match(c.bodyOutput, s.result, True) for c in s.clause),
    'ConditionalNode.executable_nodes': lambda s: set(n for c in s.clause for n in list(c.test) + list(c.body)) == set(n for n in s.node if kind(s, n, 'ExecutableNode')),
    'CreateLinkAction.association_not_abstract': lambda s: not s.association().isAbstract,
    'CreateLinkObjectAction.multiplicity': lambda s: one(s.result),
    'CreateLinkObjectAction.type_of_result': lambda s: required(s.result).type is s.association(),
    'CreateLinkObjectAction.association_class': lambda s: kind(s, s.association(), 'AssociationClass'),
    'CreateObjectAction.classifier_not_abstract': lambda s: not required(s.classifier).isAbstract,
    'CreateObjectAction.multiplicity': lambda s: one(s.result),
    'CreateObjectAction.classifier_not_association_class': lambda s: not kind(s, s.classifier, 'AssociationClass'),
    'CreateObjectAction.same_type': lambda s: required(s.result).type is required(s.classifier),
    'DestroyObjectAction.multiplicity': lambda s: one(s.target),
    'DestroyObjectAction.no_type': lambda s: required(s.target).type is None,
    'ExpansionNode.region_as_input_or_output': lambda s: (s.regionAsInput is not None) != (s.regionAsOutput is not None),
    'InputPin.outgoing_edges_structured_only': lambda s: not s.outgoing or kind(s, s.owner, 'StructuredActivityNode') and all(e.target in s.owner.allOwnedNodes() for e in s.outgoing),
    'LinkAction.same_pins': lambda s: Counter(s.inputValue) == Counter(p for d in s.endData for p in d.allPins()),
    'LinkAction.same_association': lambda s: Counter(d.end for d in s.endData) == Counter(s.association().memberEnd),
    'LinkAction.not_static': lambda s: all(not required(d.end).isStatic for d in s.endData),
    'LinkEndData.same_type': lambda s: s.value is None or conforms(s.value.type, required(s.end).type),
    'LinkEndData.multiplicity': lambda s: s.value is None or one(s.value),
    'LinkEndData.end_object_input_pin': lambda s: s.value is None or s.value not in [q.value for q in s.qualifier],
    'LinkEndData.property_is_association_end': lambda s: required(s.end).association is not None,
    'LinkEndData.qualifiers': lambda s: all(q.qualifier in required(s.end).qualifier for q in s.qualifier),
    'LinkEndDestructionData.destroyAt_pin': lambda s: s.destroyAt is None if not required(s.end).isOrdered or s.end.isUnique or s.isDestroyDuplicates else index_pin(s.destroyAt),
    'LoopNode.result_no_incoming': lambda s: all(not p.incoming for p in s.result),
    'LoopNode.input_edges': lambda s: all(not p.outgoing for p in s.loopVariableInput),
    'LoopNode.executable_nodes': lambda s: set(s.setupPart) | set(s.test) | set(s.bodyPart) == set(n for n in s.node if kind(s, n, 'ExecutableNode')),
    'LoopNode.body_output_pins': lambda s: set(s.bodyOutput) <= set(outputs(s.bodyPart)),
    'LoopNode.setup_test_and_body': lambda s: not (set(s.setupPart) & set(s.test) or set(s.setupPart) & set(s.bodyPart) or set(s.test) & set(s.bodyPart)),
    'LoopNode.matching_output_pins': lambda s: len(s.bodyOutput) == len(s.loopVariable) and all(conforms(a.type, b.type) and a.isOrdered == b.isOrdered and a.isUnique == b.isUnique and b.includesMultiplicity(a) for a, b in zip(s.bodyOutput, s.loopVariable)),
    'LoopNode.loop_variable_outgoing': lambda s: all(e.target in s.allOwnedNodes() for p in s.loopVariable for e in p.outgoing),
    'OpaqueAction.language_body_size': lambda s: not s.language or len(s.body) == len(s.language),
    'OutputPin.incoming_edges_structured_only': lambda s: not s.incoming or kind(s, s.owner, 'StructuredActivityNode') and all(e.source in s.owner.allOwnedNodes() for e in s.incoming),
    'Pin.control_pins': lambda s: not s.isControl or s.isControlType,
    'Pin.not_unique': lambda s: not s.isUnique,
    'QualifierValue.multiplicity_of_qualifier': lambda s: one(s.value),
    'QualifierValue.type_of_qualifier': lambda s: conforms(required(s.value).type, required(s.qualifier).type),
    'QualifierValue.qualifier_attribute': lambda s: s.qualifier in required(single(reverse(s, 'LinkEndData', 'qualifier'))).end.qualifier,
    'ReadExtentAction.type_is_classifier': lambda s: required(s.result).type is required(s.classifier),
    'ReadExtentAction.multiplicity_of_result': lambda s: required(s.result).is_(0, float('inf')),
    'ReadIsClassifiedObjectAction.no_type': lambda s: required(s.object).type is None,
    'ReadIsClassifiedObjectAction.multiplicity_of_output': lambda s: one(s.result),
    'ReadIsClassifiedObjectAction.boolean_result': lambda s: primitive(required(s.result).type, 'Boolean'),
    'ReadIsClassifiedObjectAction.multiplicity_of_input': lambda s: one(s.object),
    'ReadLinkAction.type_and_ordering': lambda s: all(e.type is required(s.result).type and e.isOrdered == s.result.isOrdered for e in s.openEnd()),
    'ReadLinkAction.compatible_multiplicity': lambda s: s.openEnd()[0].compatibleWith(required(s.result)),
    'ReadLinkAction.one_open_end': lambda s: len(s.openEnd()) == 1,
    'ReadLinkAction.navigable_open_end': lambda s: s.openEnd()[0].isNavigable(),
    'ReadLinkObjectEndAction.property': lambda s: required(s.end).association is not None,
    'ReadLinkObjectEndAction.multiplicity_of_object': lambda s: one(s.object),
    'ReadLinkObjectEndAction.ends_of_association': lambda s: all(not e.isStatic for e in required(s.end).association.memberEnd),
    'ReadLinkObjectEndAction.type_of_result': lambda s: required(s.result).type is required(s.end).type,
    'ReadLinkObjectEndAction.multiplicity_of_result': lambda s: one(s.result),
    'ReadLinkObjectEndAction.type_of_object': lambda s: required(s.object).type is required(s.end).association,
    'ReadLinkObjectEndAction.association_of_association': lambda s: kind(s, required(s.end).association, 'AssociationClass'),
    'ReadLinkObjectEndQualifierAction.multiplicity_of_object': lambda s: one(s.object),
    'ReadLinkObjectEndQualifierAction.type_of_object': lambda s: required(s.object).type is required(s.qualifier).associationEnd.association,
    'ReadLinkObjectEndQualifierAction.multiplicity_of_qualifier': lambda s: one(s.qualifier),
    'ReadLinkObjectEndQualifierAction.ends_of_association': lambda s: all(not e.isStatic for e in required(s.qualifier).associationEnd.association.memberEnd),
    'ReadLinkObjectEndQualifierAction.multiplicity_of_result': lambda s: one(s.result),
    'ReadLinkObjectEndQualifierAction.same_type': lambda s: required(s.result).type is required(s.qualifier).type,
    'ReadLinkObjectEndQualifierAction.association_of_association': lambda s: kind(s, required(s.qualifier).associationEnd.association, 'AssociationClass'),
    'ReadLinkObjectEndQualifierAction.qualifier_attribute': lambda s: required(s.qualifier).associationEnd is not None,
    'ReadSelfAction.contained': lambda s: s.context is not None,
    'ReadSelfAction.multiplicity': lambda s: one(s.result),
    'ReadSelfAction.not_static': lambda s: required(s.containingBehavior()).specification is None or not s.containingBehavior().specification.isStatic,
    'ReadSelfAction.type': lambda s: required(s.result).type is s.context,
    'ReadStructuralFeatureAction.multiplicity': lambda s: required(s.structuralFeature).compatibleWith(required(s.result)),
    'ReadStructuralFeatureAction.type_and_ordering': lambda s: required(s.result).type is required(s.structuralFeature).type and s.result.isOrdered == s.structuralFeature.isOrdered,
    'ReadVariableAction.type_and_ordering': lambda s: required(s.result).type is required(s.variable).type and s.result.isOrdered == s.variable.isOrdered,
    'ReadVariableAction.compatible_multiplicity': lambda s: required(s.variable).compatibleWith(required(s.result)),
    'ReclassifyObjectAction.input_pin': lambda s: required(s.object).type is None,
    'ReclassifyObjectAction.classifier_not_abstract': lambda s: all(not c.isAbstract for c in s.newClassifier),
    'ReclassifyObjectAction.multiplicity': lambda s: one(s.object),
    'ReduceAction.output_types_are_compatible': lambda s: all(conforms(p.type, required(s.result).type) for p in required(s.reducer).outputParameters()),
    'ReplyAction.pins_match_parameter': lambda s: pins_match(s.replyValue, required(s.replyToCall).event.operation.outputParameters()),
    'ReplyAction.event_on_reply_to_call_trigger': lambda s: kind(s, required(s.replyToCall).event, 'CallEvent'),
    'SendObjectAction.type_target_pin': lambda s: s.onPort is None or s.onPort in required(s.target).type.allFeatures(),
    'SendSignalAction.type_target_pin': lambda s: s.onPort is None or s.onPort in required(s.target).type.allFeatures(),
    'SendSignalAction.number_order': lambda s: len(s.argument) == len(required(s.signal).allAttributes()),
    'SendSignalAction.type_ordering_multiplicity': lambda s: pins_match(s.argument, required(s.signal).allAttributes()),
    'StartClassifierBehaviorAction.multiplicity': lambda s: one(s.object),
    'StartClassifierBehaviorAction.type_has_classifier': lambda s: required(s.object).type is None or kind(s, s.object.type, 'BehavioredClassifier') and s.object.type.classifierBehavior is not None,
    'StartObjectBehaviorAction.multiplicity_of_object': lambda s: one(s.object),
    'StartObjectBehaviorAction.type_of_object': lambda s: s.behavior() is not None,
    'StartObjectBehaviorAction.no_onport': lambda s: s.onPort is None,
    'StructuralFeatureAction.multiplicity': lambda s: one(s.object),
    'StructuralFeatureAction.not_static': lambda s: not required(s.structuralFeature).isStatic,
    'StructuralFeatureAction.one_featuring_classifier': lambda s: len(s._items(required(s.structuralFeature).featuringClassifier)) == 1,
    'StructuredActivityNode.output_pin_edges': lambda s: all(e.target not in set(s.allOwnedNodes()) - set(s.input) for p in s.output for e in p.outgoing),
    'StructuredActivityNode.input_pin_edges': lambda s: all(e.source not in set(s.allOwnedNodes()) - set(s.output) for p in s.input for e in p.incoming),
    'TestIdentityAction.multiplicity': lambda s: one(s.first) and one(s.second),
    'TestIdentityAction.no_type': lambda s: required(s.first).type is None and required(s.second).type is None,
    'TestIdentityAction.result_is_boolean': lambda s: primitive(required(s.result).type, 'Boolean'),
    'UnmarshallAction.structural_feature': lambda s: len(required(s.unmarshallType).allAttributes()) >= 1,
    'UnmarshallAction.number_of_result': lambda s: len(required(s.unmarshallType).allAttributes()) == len(s.result),
    'UnmarshallAction.type_ordering_and_multiplicity': lambda s: pins_match(required(s.unmarshallType).allAttributes(), s.result),
    'UnmarshallAction.multiplicity_of_object': lambda s: one(s.object),
    'UnmarshallAction.object_type': lambda s: conforms(required(s.object).type, required(s.unmarshallType)),
    'ValuePin.no_incoming_edges': lambda s: not s.incoming,
    'ValuePin.compatible_type': lambda s: conforms(required(s.value).type, s.type),
})


@invariant('AddStructuralFeatureValueAction.insertAt_pin', 'AddVariableValueAction.insertAt_pin', 'LinkEndCreationData.insertAt_pin')
def insert_pin(self):
    feature = getattr(self, 'structuralFeature', None) or getattr(self, 'variable', None) or getattr(self, 'end', None)
    if not required(feature).isOrdered: return self.insertAt is None
    return self.isReplaceAll or index_pin(self.insertAt)


@invariant('RemoveStructuralFeatureValueAction.removeAt_and_value', 'RemoveVariableValueAction.removeAt_and_value')
def remove_pin(self):
    feature = getattr(self, 'structuralFeature', None) or getattr(self, 'variable', None)
    if required(feature).isOrdered and not feature.isUnique and not self.isRemoveDuplicates:
        return self.value is None and index_pin(self.removeAt)
    return self.removeAt is None and self.value is not None


@invariant('LoopNode.matching_loop_variables')
def loop_variables(self): return same_pin_properties(self.loopVariableInput, self.loopVariable)


@invariant('LoopNode.matching_result_pins')
def loop_results(self): return same_pin_properties(self.result, self.loopVariable)


def same_pin_properties(a, b):
    fields = ('type', 'isUnique', 'lower', 'upper')
    return len(a) == len(b) and all(all(getattr(x, f) == getattr(y, f) for f in fields) for x, y in zip(a, b))


@invariant('ConditionalNode.clause_no_predecessor')
def clause_cycles(self):
    # The published closure mistakenly includes direct predecessors in the rejection.
    # Reject cycles; an acyclic predecessor in this same conditional node is valid.
    def cyclic(start):
        seen, pending = set(), list(start.predecessorClause)
        while pending:
            clause = pending.pop()
            if clause is start: return True
            if clause in seen: continue
            seen.add(clause)
            pending.extend(clause.predecessorClause)
        return False
    return not any(cyclic(c) for c in self.clause)


@invariant('CallOperationAction.type_target_pin')
def call_target(self):
    features = required(self.target).type.allFeatures()
    if self.onPort is None: return self.operation in features
    return self.onPort in features and any(self.operation in i.allFeatures() for i in list(self.onPort.provided) + list(self.onPort.required))


@invariant('AcceptEventAction.unmarshall_signal_events')
def unmarshall_signal(self):
    if not self.isUnmarshall or type(self) is not self.__registry__['AcceptEventAction']: return True
    if len(self.trigger) != 1 or not kind(self, self.trigger[0].event, 'SignalEvent'): return False
    attributes = required(self.trigger[0].event.signal).allAttributes()
    return bool(attributes) and len(self.result) == len(attributes) and all(p.type is a.type and p.isOrdered == a.isOrdered and p.includesMultiplicity(a) for p, a in zip(self.result, attributes))


@invariant('AcceptEventAction.conforming_type')
def accept_type(self):
    if self.isUnmarshall or not self.result or self.result[0].type is None: return True
    return all(kind(self, t.event, 'SignalEvent') and t.event.signal.conformsTo(self.result[0].type) for t in self.trigger)


@invariant('ReduceAction.reducer_inputs_output')
def reducer_parameters(self):
    inputs, outputs_ = required(self.reducer).inputParameters(), self.reducer.outputParameters()
    return len(inputs) == 2 and len(outputs_) == 1 and all(conforms(outputs_[0].type, p.type) and (upper_bound(required(self.collection)) <= 1 or conforms(self.collection.type, p.type)) for p in inputs)


@invariant('StructuralFeatureAction.object_type')
def structural_object(self):
    type_, feature = required(self.object).type, required(self.structuralFeature)
    return feature in required(type_).allFeatures() or kind(self, feature, 'Property') and conforms(type_, required(feature.opposite).type)


@invariant('StructuralFeatureAction.visibility')
def structural_visibility(self):
    f = required(self.structuralFeature)
    return enum(f.visibility) == 'public' or f in required(self.context).allFeatures() or enum(f.visibility) == 'protected' and kind(self, f, 'Property') and conforms(self.context, required(f.opposite).type)


@invariant('WriteLinkAction.allow_access')
def write_access(self):
    ends = [required(d.end) for d in self.endData]
    return any(e.type is self.context or enum(e.visibility) == 'public' or enum(e.visibility) == 'protected' and any(other is not e and conforms(self.context, other.type) for other in ends) for e in ends)


@invariant('ReadLinkAction.visibility')
def read_access(self):
    end = self.openEnd()[0]
    return enum(end.visibility) == 'public' or any(d.end is not end and (self.context is d.end.type or enum(end.visibility) == 'protected' and conforms(self.context, d.end.type)) for d in self.endData)


@invariant('StructuredActivityNode.edges')
def structured_edges(self):
    nodes = self.allOwnedNodes()
    outgoing = {e for n in nodes for e in n.outgoing}
    incoming = {e for n in nodes for e in n.incoming}
    expected = ({e for n in self.sourceNodes() for e in n.outgoing} & incoming) | ({e for n in self.targetNodes() for e in n.incoming} & outgoing)
    return set(self.edge) == expected
