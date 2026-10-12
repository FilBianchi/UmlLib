"""Explicit Python predicates for value, classifier and use-case constraints."""
from . import invariant, kind, instances, reverse, single, NativeNotImplemented
from .state_machines import protocol_regions


def enum(value): return None if value is None else value.value
def required(value):
    if value is None: raise ValueError('Required UML reference is absent')
    return value


def predicates(definitions):
    for identifier, predicate in definitions.items():
        invariant(identifier)(predicate)


predicates({
    'Duration.no_expr_requires_observation': lambda s: s.expr is not None or len(s.observation) == 1 and kind(s, s.observation[0], 'DurationObservation'),
    'DurationConstraint.first_event_multiplicity': lambda s: len(s.firstEvent) == (2 if len(s.constrainedElement) == 2 else 0),
    'DurationConstraint.has_one_or_two_constrainedElements': lambda s: len(s.constrainedElement) in (1, 2),
    'DurationObservation.first_event_multiplicity': lambda s: len(s.firstEvent) == (2 if len(s.event) == 2 else 0),
    'OpaqueExpression.language_body_size': lambda s: not s.language or len(s.body) == len(s.language),
    'OpaqueExpression.one_return_result_parameter': lambda s: s.behavior is None or sum(enum(p.direction) == 'return' for p in s.behavior.ownedParameter) == 1,
    'OpaqueExpression.only_in_or_return_parameters': lambda s: s.behavior is None or all(not p.isStream and enum(p.direction) in ('in', 'return') for p in s.behavior.ownedParameter),
    'StringExpression.operands': lambda s: all(kind(s, p, 'LiteralString') for p in s.operand),
    'StringExpression.subexpressions': lambda s: not s.operand if s.subExpression else bool(s.operand),
    'TimeConstraint.has_one_constrainedElement': lambda s: len(s.constrainedElement) == 1,
    'TimeExpression.no_expr_requires_observation': lambda s: s.expr is not None or len(s.observation) == 1 and kind(s, s.observation[0], 'TimeObservation'),
    'Actor.must_have_name': lambda s: s.name is not None,
    'ExtensionPoint.must_have_name': lambda s: s.name is not None,
    'UseCase.must_have_name': lambda s: s.name is not None,
    'UseCase.cannot_include_self': lambda s: s not in s.allIncludedUseCases(),
    'UseCase.binary_associations': lambda s: all(len(a.memberEnd) == 2 for a in instances(s, 'Association') if s in [e.type for e in a.memberEnd]),
    'Extend.extension_points': lambda s: all(x in required(s.extendedCase).extensionPoint for x in s.extensionLocation),
    'AssociationClass.cannot_be_defined': lambda s: s not in s.endType and all(s not in required(t).allParents() for t in s.endType),
    'AssociationClass.disjoint_attributes_ends': lambda s: not set(s.ownedAttribute) & set(s.ownedEnd),
    'Class.passive_class': lambda s: s.isActive or not s.ownedReception and s.classifierBehavior is None,
    'Component.no_nested_classifiers': lambda s: not s.nestedClassifier,
    'Component.no_packaged_elements': lambda s: not reverse(s, 'Class', 'nestedClassifier') or not s.packagedElement,
    'ConnectorEnd.self_part_with_port': lambda s: s.partWithPort is None or not kind(s, s.partWithPort, 'Port'),
    'ConnectorEnd.role_and_part_with_port': lambda s: s.partWithPort is None or kind(s, s.role, 'Port') and s.role in required(s.partWithPort.type).member,
    'ConnectorEnd.part_with_port_empty': lambda s: not (kind(s, s.role, 'Port') and s.role.owner is required(s.owner).owner) or s.partWithPort is None,
    'ConnectorEnd.multiplicity': lambda s: s.definingEnd is None or s.compatibleWith(s.definingEnd),
    'Port.port_aggregation': lambda s: enum(s.aggregation) == 'composite',
    'Port.default_value': lambda s: not kind(s, s.type, 'Interface') or s.defaultValue is None,
    'Port.encapsulated_owner': lambda s: kind(s, s.owner, 'EncapsulatedClassifier') and s in s.owner.ownedPort,
    'BehavioredClassifier.class_behavior': lambda s: s.classifierBehavior is None or s.classifierBehavior.specification is None,
    'Enumeration.immutable': lambda s: all(a.isReadOnly for a in s.ownedAttribute),
    'Interface.visibility': lambda s: all(enum(f.visibility) == 'public' for f in s.feature),
    'Reception.same_name_as_signal': lambda s: s.name == required(s.signal).name,
    'Extension.is_binary': lambda s: len(s.memberEnd) == 2,
    'Extension.non_owned_end': lambda s: kind(s, s.metaclassEnd().type, 'Class'),
    'Stereotype.binaryAssociationsOnly': lambda s: all(len(a.association.memberEnd) == 2 for a in s.ownedAttribute if a.association is not None),
    'Stereotype.generalize': lambda s: all(kind(s, p, 'Stereotype') for p in s.allParents()) and all(kind(s, c, 'Stereotype') for c in instances(s, 'Classifier') if any(kind(s, p, 'Stereotype') for p in c.allParents())),
    'Stereotype.associationEndOwnership': lambda s: all(required(a.opposite).owner is a.association for a in s.ownedAttribute if a.association is not None and not kind(s, a.association, 'Extension') and not kind(s, a.type, 'Stereotype')),
    'CommunicationPath.association_ends': lambda s: all(kind(s, t, 'DeploymentTarget') for t in s.endType),
    'DeploymentSpecification.deployment_target': lambda s: all(kind(s, d.location, 'ExecutionEnvironment') for d in reverse(s, 'Deployment', 'configuration')),
    'DeploymentSpecification.deployed_elements': lambda s: all(kind(s, e, 'Component') for d in reverse(s, 'Deployment', 'configuration') for e in required(d.location).deployedElement),
    'Node.internal_structure': lambda s: all(kind(s, p.type, 'Node') for p in s.part),
    'FunctionBehavior.one_output_parameter': lambda s: bool(s.outputParameters()),
    'FunctionBehavior.types_of_parameters': lambda s: all(type(p.type) is s.__registry__['DataType'] and s.hasAllDataTypeAttributes(p.type) for p in s.ownedParameter),
    'Trigger.trigger_with_ports': lambda s: not s.port or kind(s, s.event, 'MessageEvent'),
    'ProtocolStateMachine.classifier_context': lambda s: s.context is not None and s.specification is None,
    'ProtocolStateMachine.deep_or_shallow_history': lambda s: all(enum(v.kind) not in ('deepHistory', 'shallowHistory') for r in protocol_regions(s) for v in r.subvertex if kind(s, v, 'Pseudostate')),
    'ProtocolStateMachine.entry_exit_do': lambda s: all(v.entry is None and v.exit is None and v.doActivity is None for r in protocol_regions(s) for v in r.subvertex if kind(s, v, 'State')),
    'ProtocolStateMachine.protocol_transitions': lambda s: all(type(t) is s.__registry__['ProtocolTransition'] for r in protocol_regions(s) for t in r.transition),
    'ProtocolTransition.refers_to_operation': lambda s: not s.referred or s.containingStateMachine().context is None or all(o in s.containingStateMachine().context.allFeatures() for o in s.referred),
    'ProtocolTransition.associated_actions': lambda s: s.effect is None,
    'ProtocolTransition.belongs_to_psm': lambda s: required(s.container).belongsToPSM(),
    'Constraint.not_apply_to_self': lambda s: s not in s.constrainedElement,
    'PackageableElement.namespace_needs_visibility': lambda s: s.visibility is not None or s.namespace is None,
    'TemplateBinding.parameter_substitution_formal': lambda s: all(b.formal in required(s.signature).parameter for b in s.parameterSubstitution),
    'TemplateBinding.one_parameter_substitution': lambda s: all(sum(b.formal is p for b in s.parameterSubstitution) <= 1 for p in required(s.signature).parameter),
    'TemplateParameter.must_be_compatible': lambda s: s.default is None or s.default.isCompatibleWith(required(s.parameteredElement)),
    'TemplateParameterSubstitution.must_be_compatible': lambda s: all(a.isCompatibleWith(required(s.formal).parameteredElement) for a in s._items(s.actual)),
    'TemplateSignature.own_elements': lambda s: all(p.parameteredElement in required(s.template).ownedElement for p in s.parameter if p.parameteredElement not in [q.ownedParameteredElement for q in s.parameter]),
    'BehavioralFeature.abstract_no_method': lambda s: not s.isAbstract or not s.method,
    'ClassifierTemplateParameter.has_constraining_classifier': lambda s: not s.allowSubstitutable or bool(s.constrainingClassifier),
    'ClassifierTemplateParameter.parametered_element_no_features': lambda s: not required(s.parameteredElement).feature and (bool(s.constrainingClassifier) or not s.parameteredElement.allParents()),
    'ClassifierTemplateParameter.actual_is_classifier': lambda s: all(kind(s, a.actual, 'Classifier') for a in reverse(s, 'TemplateParameterSubstitution', 'formal')),
    'ClassifierTemplateParameter.matching_abstract': lambda s: required(s.parameteredElement).isAbstract or all(not required(a.actual).isAbstract for a in reverse(s, 'TemplateParameterSubstitution', 'formal')),
    'GeneralizationSet.generalization_same_classifier': lambda s: len(set(g.general for g in s.generalization)) <= 1,
    'GeneralizationSet.maps_to_generalization_set': lambda s: s.powertype is None or all(g.general is not s.powertype and s.powertype not in required(g.general).allParents() and g.specific is not s.powertype and g.specific not in s.powertype.allParents() for g in s.generalization),
    'InstanceSpecification.deployment_artifact': lambda s: not reverse(s, 'Deployment', 'deployedArtifact') or any(kind(s, c, 'Artifact') for c in s.classifier),
    'InstanceSpecification.structural_feature': lambda s: all(sum(slot.definingFeature is f for slot in s.slot) <= 1 for c in s.classifier for f in c.allSlottableFeatures()),
    'InstanceSpecification.defining_feature': lambda s: all(any(slot.definingFeature in c.allSlottableFeatures() for c in s.classifier) for slot in s.slot),
    'InstanceSpecification.deployment_target': lambda s: not s.deployment or any(kind(s, c, 'Node') and any(p.type is c for n in instances(s, 'Node') for p in n.part) for c in s.classifier),
    'Operation.at_most_one_return': lambda s: sum(enum(p.direction) == 'return' for p in s.ownedParameter) <= 1,
    'Operation.only_body_for_query': lambda s: s.bodyCondition is None or s.isQuery,
    'Parameter.in_and_out': lambda s: (enum(s.effect) != 'delete' or enum(s.direction) in ('in', 'inout')) and (enum(s.effect) != 'create' or enum(s.direction) in ('out', 'inout', 'return')),
    'Parameter.not_exception': lambda s: not s.isException or enum(s.direction) not in ('in', 'inout'),
    'Parameter.connector_end': lambda s: not s.end or bool(reverse(s, 'Collaboration', 'collaborationRole')),
    'Parameter.reentrant_behaviors': lambda s: not s.isStream or all(not b.isReentrant for b in reverse(s, 'Behavior', 'ownedParameter')),
    'Parameter.stream_and_exception': lambda s: not (s.isException and s.isStream),
    'Parameter.object_effect': lambda s: not kind(s, s.type, 'DataType') or s.effect is None,
    'ParameterSet.same_parameterized_entity': lambda s: all(p.owner is s.owner for p in s.parameter) and len(set(p.direction for p in s.parameter)) <= 1,
    'Property.derived_union_is_read_only': lambda s: not s.isDerivedUnion or s.isReadOnly,
    'Property.derived_union_is_derived': lambda s: not s.isDerivedUnion or s.isDerived,
    'Property.multiplicity_of_composite': lambda s: not s.isComposite or s.association is None or required(s.opposite).upperBound() <= 1,
    'Property.subsetting_rules': lambda s: all(required(s.type).conformsTo(required(p.type)) and s.upperBound() <= p.upperBound() for p in s.subsettedProperty),
    'Property.subsetted_property_names': lambda s: all(p.name != s.name for p in s.subsettedProperty),
    'Property.qualified_is_association_end': lambda s: not s.qualifier or s.association is not None,
    'Property.type_of_opposite_end': lambda s: s.opposite is None or s.owningAssociation is not None or s.owner is s.opposite.type,
    'Property.binding_to_attribute': lambda s: not s.isAttribute() or all(kind(s, ts.formal.parameteredElement, 'Property') and ts.formal.parameteredElement.isAttribute() for ts in reverse(s, 'TemplateParameterSubstitution', 'actual')),
    'Property.deployment_target': lambda s: not s.deployment or kind(s, s.owner, 'Node') and any(s in n.part for n in instances(s, 'Node')),
})


@invariant('TimeEvent.when_non_negative')
def nonnegative_time(self):
    expression = required(self.when)
    value = expression.integerValue()
    if value is None:
        # TimeExpression has no integerValue override in the XMI. A represented
        # computable expr supplies static evidence without executing a language.
        expr = expression.expr
        if expr is None or not expr.isComputable():
            raise NativeNotImplemented('TimeExpression requires an integer evaluation or observation adapter')
        value = expr.integerValue()
    return value is not None and value >= 0


@invariant('Actor.associations')
def actor_associations(self):
    for association in instances(self, 'Association'):
        if self not in [end.type for end in association.memberEnd]: continue
        if len(association.memberEnd) != 2: return False
        other = next(end for end in association.memberEnd if end.type is not self) if any(end.type is not self for end in association.memberEnd) else association.memberEnd[0]
        if not (kind(self, other.type, 'UseCase') or kind(self, other.type, 'Class') and not kind(self, other.type, 'Behavior')): return False
    return True


@invariant('UseCase.no_association_to_use_case')
def use_case_subjects(self):
    for association in instances(self, 'Association'):
        if self not in [e.type for e in association.memberEnd]: continue
        cases = set(e.type for e in association.memberEnd if kind(self, e.type, 'UseCase'))
        if any(set(a.subject) & set(b.subject) for a in cases for b in cases if a is not b): return False
    return True


@invariant('Reception.same_structure_as_signal')
def reception_parameters(self):
    attributes = required(self.signal).ownedAttribute
    return len(attributes) == len(self.ownedParameter) and all(enum(p.direction) == 'in' and p.name == a.name and p.type is a.type and p.lowerBound() == a.lowerBound() and p.upperBound() == a.upperBound() for p, a in zip(self.ownedParameter, attributes))


@invariant('Connector.types')
def connector_types(self):
    return self.type is None or len(self.end) == len(self.type.memberEnd) and all(required(e.role).type.conformsTo(required(p.type)) for e, p in zip(self.end, self.type.memberEnd))


@invariant('Connector.roles')
def connector_roles(self):
    if not kind(self, self.owner, 'StructuredClassifier'): return False
    roles = self.owner.allRoles()
    return all(e.role in roles or kind(self, e.role, 'Port') and e.partWithPort in roles for e in self.end)


@invariant('TemplateSignature.unique_parameters')
def unique_parameters(self):
    named = [p.parameteredElement for p in self.parameter if kind(self, p.parameteredElement, 'NamedElement')]
    return len([p.name for p in named]) == len(set(p.name for p in named))


@invariant('ClassifierTemplateParameter.constraining_classifiers_constrain_args')
def constrained_arguments(self):
    values = [ts.actual for ts in reverse(self, 'TemplateParameterSubstitution', 'formal')]
    return all(arg is cc or arg.conformsTo(cc) or self.allowSubstitutable and arg.isSubstitutableFor(cc) for arg in values for cc in self.constrainingClassifier)


@invariant('ClassifierTemplateParameter.constraining_classifiers_constrain_parametered_element')
def constrained_formal(self):
    formal = required(self.parameteredElement)
    return all(formal is cc or formal.conformsTo(cc) or self.allowSubstitutable and formal.isSubstitutableFor(cc)
               for cc in self.constrainingClassifier)


@invariant('OperationTemplateParameter.match_default_signature')
def default_signature(self):
    if self.default is None: return True
    if not kind(self, self.default, 'Operation'): return False
    parameters = required(self.parameteredElement).ownedParameter
    fields = ('type', 'upper', 'lower', 'direction', 'isOrdered', 'isUnique')
    return len(parameters) == len(self.default.ownedParameter) and all(all(getattr(a, f) == getattr(b, f) for f in fields) for a, b in zip(parameters, self.default.ownedParameter))


@invariant('Property.subsetting_context_conforms')
def subsetting_contexts(self):
    if not self.subsettedProperty: return True
    contexts = self.subsettingContext()
    return bool(contexts) and all(any(sc.conformsTo(c) for c in sp.subsettingContext()) for sc in contexts for sp in self.subsettedProperty)


@invariant('Property.redefined_property_inherited')
def inherited_redefinition(self):
    if not self.redefinedProperty: return True
    contexts = self._items(self.redefinitionContext)
    features = [f for c in contexts for p in c.allParents() for f in p.allFeatures()]
    return bool(contexts) and all(p in features for p in self.redefinedProperty)


@invariant('RedefinableTemplateSignature.redefines_parents')
def signature_parents(self):
    extended, pending = set(), list(self.extendedSignature)
    while pending:
        signature = pending.pop()
        if signature in extended: continue
        extended.add(signature)
        pending.extend(signature.extendedSignature)
    return all(p.ownedTemplateSignature is None or p.ownedTemplateSignature in extended for p in required(self.classifier).allParents())
