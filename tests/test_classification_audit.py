"""Classification scenarios with outcomes derived from the shipped UML rules."""
import unittest
import Uml
from umltools import ModelSession
from umltools.native import check
from semantic_cases import verifies


def bounded(cls, lower=1, upper=1, **kwargs):
    return cls(lowerValue=Uml.LiteralInteger(value=lower), upperValue=Uml.LiteralUnlimitedNatural(value=upper), **kwargs)


class ClassificationCases(unittest.TestCase):
    def setUp(self):
        self.scope = ModelSession()
        self.scope.__enter__()

    def tearDown(self): self.scope.__exit__(None, None, None)

    @verifies('Classifier.parents', 'Classifier.general', 'Classifier.allParents', 'Classifier.maySpecializeType',
              'Classifier.specialize_type', 'Classifier.non_final_parents', 'Classifier.no_cycles_in_generalization',
              'Classifier.isTemplate', 'Classifier.hasVisibilityOf', 'Classifier.inheritableMembers',
              'Classifier.inherit', 'Classifier.inheritedMember', 'Classifier.allFeatures', 'Classifier.allAttributes', 'Classifier.allSlottableFeatures',
              'Classifier-hasVisibilityOf-pre', 'Classifier-inheritableMembers-pre', 'Classifier-feature')
    def test_inheritance_visibility_redefinition_templates_and_cycles(self):
        base, child = Uml.Class(name='Base'), Uml.Class(name='Child')
        child.generalization.append(Uml.Generalization(general=base))
        public, private = Uml.Property(name='a'), Uml.Property(name='secret', visibility=Uml.VisibilityKind.private)
        base.ownedAttribute.extend([public, private])
        self.assertEqual(child.parents(), [base])
        self.assertEqual(list(child.general), [base])
        self.assertEqual(child.allParents(), [base])
        self.assertTrue(child.maySpecializeType(base))
        self.assertFalse(child.maySpecializeType(Uml.Interface()))
        self.assertTrue(check(child, 'Classifier.specialize_type'))
        self.assertEqual(base.inheritableMembers(child), [public])
        self.assertTrue(child.hasVisibilityOf(public))
        self.assertFalse(child.hasVisibilityOf(private))
        with self.assertRaises(ValueError): child.hasVisibilityOf(Uml.Property())
        with self.assertRaises(ValueError): base.inheritableMembers(Uml.Class())
        self.assertIn(public, child.allFeatures())
        self.assertEqual(set(base.feature), {public, private})
        self.assertEqual(child.allAttributes(), [public])
        self.assertIn(private, child.allSlottableFeatures())  # Explicit all-parent attributes in the XMI body.
        replacement = Uml.Property(name='a', redefinedProperty=[public])
        child.ownedAttribute.append(replacement)
        self.assertEqual(child.inherit([public, private]), [private])
        self.assertNotIn(public, child.inheritedMember)
        self.assertFalse(child.isTemplate())
        base.ownedTemplateSignature = Uml.RedefinableTemplateSignature()
        self.assertTrue(child.isTemplate())
        base.isFinalSpecialization = True
        self.assertFalse(check(child, 'Classifier.non_final_parents'))
        child.generalization.append(Uml.Generalization(general=Uml.Interface()))
        self.assertFalse(check(child, 'Classifier.specialize_type'))
        base.generalization.append(Uml.Generalization(general=child))
        self.assertFalse(check(child, 'Classifier.no_cycles_in_generalization'))
        base.ownedTemplateSignature = None
        with self.assertRaises(ValueError): base.isTemplate()

    @verifies('Classifier.directlyRealizedInterfaces', 'Classifier.directlyUsedInterfaces',
              'Classifier.allRealizedInterfaces', 'Classifier.allUsedInterfaces', 'Classifier.isSubstitutableFor')
    def test_realized_used_interfaces_and_substitution_are_distinct(self):
        base, child, realized, used = Uml.Class(), Uml.Class(), Uml.Interface(), Uml.Interface()
        child.generalization.append(Uml.Generalization(general=base))
        usage = Uml.Usage(client=[child], supplier=[used])
        realization = Uml.Realization(client=[base], supplier=[realized])
        self.assertEqual(base.directlyRealizedInterfaces(), [realized])
        self.assertEqual(child.allRealizedInterfaces(), [realized])
        self.assertEqual(child.directlyUsedInterfaces(), [used])
        self.assertEqual(child.allUsedInterfaces(), [used])
        self.assertEqual(used.directlyUsedInterfaces(), [])
        usage.supplier.append(Uml.Class())
        self.assertEqual(child.directlyUsedInterfaces(), [])
        self.assertFalse(child.isSubstitutableFor(base))
        child.substitution.append(Uml.Substitution(contract=base))
        self.assertTrue(child.isSubstitutableFor(base))

    @verifies('GeneralizationSet.generalization_same_classifier', 'GeneralizationSet.maps_to_generalization_set', 'Classifier.maps_to_generalization_set')
    def test_generalization_sets_share_one_general_and_exclude_powertype_cycles(self):
        base, one, two, power = [Uml.Class() for _ in range(4)]
        a, b = Uml.Generalization(general=base, specific=one), Uml.Generalization(general=base, specific=two)
        group = Uml.GeneralizationSet(generalization=[a, b], powertype=power)
        self.assertTrue(check(group, 'GeneralizationSet.generalization_same_classifier'))
        self.assertTrue(check(group, 'GeneralizationSet.maps_to_generalization_set'))
        self.assertTrue(check(power, 'Classifier.maps_to_generalization_set'))
        b.general = two
        self.assertFalse(check(group, 'GeneralizationSet.generalization_same_classifier'))
        group.powertype = base
        self.assertFalse(check(group, 'GeneralizationSet.maps_to_generalization_set'))
        self.assertFalse(check(base, 'Classifier.maps_to_generalization_set'))

    @verifies('ClassifierTemplateParameter.has_constraining_classifier', 'ClassifierTemplateParameter.parametered_element_no_features',
              'ClassifierTemplateParameter.matching_abstract', 'ClassifierTemplateParameter.actual_is_classifier',
              'ClassifierTemplateParameter.constraining_classifiers_constrain_args',
              'ClassifierTemplateParameter.constraining_classifiers_constrain_parametered_element')
    def test_classifier_template_formal_and_actual_constraints_are_independent(self):
        constraint, formal, actual = Uml.Class(), Uml.Class(), Uml.Class()
        parameter = Uml.ClassifierTemplateParameter(parameteredElement=formal)
        self.assertFalse(check(parameter, 'ClassifierTemplateParameter.has_constraining_classifier'))
        parameter.constrainingClassifier.append(constraint)
        self.assertTrue(check(parameter, 'ClassifierTemplateParameter.has_constraining_classifier'))
        actual.generalization.append(Uml.Generalization(general=constraint))
        substitution = Uml.TemplateParameterSubstitution(formal=parameter, actual=actual)
        self.assertTrue(check(parameter, 'ClassifierTemplateParameter.constraining_classifiers_constrain_args'))
        self.assertFalse(check(parameter, 'ClassifierTemplateParameter.constraining_classifiers_constrain_parametered_element'))
        formal.generalization.append(Uml.Generalization(general=constraint))
        actual.generalization.clear()
        self.assertTrue(check(parameter, 'ClassifierTemplateParameter.constraining_classifiers_constrain_parametered_element'))
        self.assertFalse(check(parameter, 'ClassifierTemplateParameter.constraining_classifiers_constrain_args'))
        actual.substitution.append(Uml.Substitution(contract=constraint))
        self.assertTrue(check(parameter, 'ClassifierTemplateParameter.constraining_classifiers_constrain_args'))
        parameter.allowSubstitutable = False
        self.assertFalse(check(parameter, 'ClassifierTemplateParameter.constraining_classifiers_constrain_args'))
        self.assertTrue(check(parameter, 'ClassifierTemplateParameter.parametered_element_no_features'))
        formal.ownedAttribute.append(Uml.Property())
        self.assertFalse(check(parameter, 'ClassifierTemplateParameter.parametered_element_no_features'))
        actual.isAbstract = True
        self.assertFalse(check(parameter, 'ClassifierTemplateParameter.matching_abstract'))
        formal.isAbstract = True
        self.assertTrue(check(parameter, 'ClassifierTemplateParameter.matching_abstract'))
        substitution.actual = Uml.Operation()
        self.assertFalse(check(parameter, 'ClassifierTemplateParameter.actual_is_classifier'))

    @verifies('RedefinableElement.isRedefinitionContextValid', 'RedefinableElement.isConsistentWith',
              'RedefinableElement.redefinition_context_valid', 'RedefinableElement.redefinition_consistent', 'RedefinableElement.non_leaf_redefinition',
              'Property.isConsistentWith', 'Property.redefined_property_inherited', 'Property-isConsistentWith-pre',
              'RedefinableElement-isConsistentWith-pre', 'RedefinableElement-redefinedElement', 'RedefinableElement-redefinitionContext')
    def test_redefinition_context_leaf_status_and_property_bounds(self):
        base, child, type_ = Uml.Class(), Uml.Class(), Uml.Class()
        child.generalization.append(Uml.Generalization(general=base))
        original = bounded(Uml.Property, 0, 5, name='x', type=type_)
        replacement = bounded(Uml.Property, 1, 3, name='x', type=type_, redefinedProperty=[original])
        base.ownedAttribute.append(original)
        child.ownedAttribute.append(replacement)
        self.assertTrue(replacement.isRedefinitionContextValid(original))
        self.assertEqual(list(replacement.redefinedElement), [original])
        self.assertEqual(list(replacement.redefinitionContext), [child])
        self.assertTrue(check(replacement, 'RedefinableElement.redefinition_context_valid'))
        self.assertTrue(check(replacement, 'RedefinableElement.redefinition_consistent'))
        self.assertTrue(check(replacement, 'Property.redefined_property_inherited'))
        self.assertFalse(original.uml_operation('RedefinableElement', 'isConsistentWith', replacement))
        original.isLeaf = True
        self.assertFalse(check(replacement, 'RedefinableElement.non_leaf_redefinition'))
        replacement.upperValue.value = 6
        self.assertFalse(original.isConsistentWith(replacement))
        self.assertFalse(check(replacement, 'RedefinableElement.redefinition_consistent'))
        child.generalization.clear()
        self.assertFalse(check(replacement, 'Property.redefined_property_inherited'))
        self.assertFalse(check(replacement, 'RedefinableElement.redefinition_context_valid'))
        with self.assertRaises(ValueError): original.isConsistentWith(replacement)

    @verifies('Property.isComposite', 'Property.isAttribute', 'Property.isNavigable', 'Property.opposite', 'Property.subsettingContext',
              'Property.multiplicity_of_composite', 'Property.type_of_opposite_end', 'Property.qualified_is_association_end')
    def test_attribute_and_association_navigation_composition_and_qualifiers(self):
        left, right = Uml.Class(), Uml.Class()
        a, b = bounded(Uml.Property, type=right), bounded(Uml.Property, type=left)
        left.ownedAttribute.append(a)
        association = Uml.Association(ownedEnd=[b], memberEnd=[a, b])
        self.assertTrue(a.isAttribute())
        self.assertTrue(a.isNavigable())
        self.assertFalse(b.isNavigable())
        association.navigableOwnedEnd.append(b)
        self.assertTrue(b.isNavigable())
        self.assertIs(a.opposite, b)
        self.assertEqual(a.subsettingContext(), [left])
        self.assertTrue(check(a, 'Property.type_of_opposite_end'))
        b.type = right
        self.assertFalse(check(a, 'Property.type_of_opposite_end'))
        a.aggregation = Uml.AggregationKind.composite
        self.assertTrue(a.isComposite)
        self.assertTrue(check(a, 'Property.multiplicity_of_composite'))
        b.upperValue.value = 2
        self.assertFalse(check(a, 'Property.multiplicity_of_composite'))
        qualifier = Uml.Property()
        a.qualifier.append(qualifier)
        self.assertTrue(check(a, 'Property.qualified_is_association_end'))
        association.memberEnd.remove(a)
        self.assertFalse(check(a, 'Property.qualified_is_association_end'))
        self.assertIsNone(a.opposite)

    @verifies('Property.subsetting_rules', 'Property.subsetting_context_conforms', 'Property.subsetted_property_names',
              'Property.derived_union_is_read_only', 'Property.derived_union_is_derived', 'Property.isCompatibleWith', 'Property.binding_to_attribute')
    def test_subsets_unions_and_attribute_template_binding(self):
        owner, child, type_, subtype = [Uml.Class() for _ in range(4)]
        child.generalization.append(Uml.Generalization(general=owner))
        subtype.generalization.append(Uml.Generalization(general=type_))
        broad, narrow = bounded(Uml.Property, 0, 5, name='all', type=type_), bounded(Uml.Property, 1, 2, name='some', type=subtype)
        owner.ownedAttribute.append(broad)
        child.ownedAttribute.append(narrow)
        narrow.subsettedProperty.append(broad)
        for rule in ('subsetting_rules', 'subsetting_context_conforms', 'subsetted_property_names'):
            self.assertTrue(check(narrow, 'Property.' + rule))
        self.assertTrue(narrow.isCompatibleWith(broad))
        self.assertFalse(broad.isCompatibleWith(narrow))
        narrow.upperValue.value = 6
        self.assertFalse(check(narrow, 'Property.subsetting_rules'))
        narrow.name = 'all'
        self.assertFalse(check(narrow, 'Property.subsetted_property_names'))
        child.generalization.clear()
        self.assertFalse(check(narrow, 'Property.subsetting_context_conforms'))
        narrow.isDerivedUnion = True
        self.assertFalse(check(narrow, 'Property.derived_union_is_read_only'))
        self.assertFalse(check(narrow, 'Property.derived_union_is_derived'))
        narrow.isReadOnly = narrow.isDerived = True
        self.assertTrue(check(narrow, 'Property.derived_union_is_read_only'))
        self.assertTrue(check(narrow, 'Property.derived_union_is_derived'))
        formal = Uml.TemplateParameter(parameteredElement=broad)
        substitution = Uml.TemplateParameterSubstitution(formal=formal, actual=narrow)
        self.assertTrue(check(narrow, 'Property.binding_to_attribute'))
        formal.parameteredElement = Uml.Property()
        self.assertFalse(check(narrow, 'Property.binding_to_attribute'))

    @verifies('Property.deployment_target', 'InstanceSpecification.deployment_target', 'InstanceSpecification.deployment_artifact')
    def test_deployment_roles_require_part_nodes_and_artifact_classifiers(self):
        node_type, node = Uml.Node(), Uml.Node()
        part = Uml.Property(type=node_type, aggregation=Uml.AggregationKind.composite)
        node.ownedAttribute.append(part)
        deployment = Uml.Deployment(location=part)
        self.assertTrue(check(part, 'Property.deployment_target'))
        ordinary = Uml.Class()
        node.ownedAttribute.remove(part)
        ordinary.ownedAttribute.append(part)
        self.assertFalse(check(part, 'Property.deployment_target'))
        node.ownedAttribute.append(Uml.Property(type=node_type, aggregation=Uml.AggregationKind.composite))
        instance = Uml.InstanceSpecification(classifier=[node_type])
        instance.deployment.append(Uml.Deployment())
        self.assertTrue(check(instance, 'InstanceSpecification.deployment_target'))
        instance.classifier = [ordinary]
        self.assertFalse(check(instance, 'InstanceSpecification.deployment_target'))
        artifact = Uml.InstanceSpecification(classifier=[Uml.Artifact()])
        deployment.deployedArtifact.append(artifact)
        self.assertTrue(check(artifact, 'InstanceSpecification.deployment_artifact'))
        artifact.classifier = [ordinary]
        self.assertFalse(check(artifact, 'InstanceSpecification.deployment_artifact'))

    @verifies('InstanceSpecification.structural_feature', 'InstanceSpecification.defining_feature')
    def test_slots_are_unique_and_belong_to_classifier_features(self):
        type_, feature, unrelated = Uml.Class(), Uml.Property(), Uml.Property()
        type_.ownedAttribute.append(feature)
        instance = Uml.InstanceSpecification(classifier=[type_], slot=[Uml.Slot(definingFeature=feature)])
        self.assertTrue(check(instance, 'InstanceSpecification.structural_feature'))
        self.assertTrue(check(instance, 'InstanceSpecification.defining_feature'))
        second = Uml.Slot(definingFeature=feature)
        instance.slot.append(second)
        self.assertFalse(check(instance, 'InstanceSpecification.structural_feature'))
        second.definingFeature = unrelated
        self.assertFalse(check(instance, 'InstanceSpecification.defining_feature'))

    @verifies('BehavioralFeature.inputParameters', 'BehavioralFeature.outputParameters', 'BehavioralFeature.isDistinguishableFrom',
              'BehavioralFeature.abstract_no_method', 'Operation.at_most_one_return', 'Operation.only_body_for_query',
              'Operation.returnResult', 'Operation.isOrdered', 'Operation.isUnique', 'Operation.lower', 'Operation.upper', 'Operation.type')
    def test_operation_signature_derived_properties_and_overload_distinction(self):
        type_ = Uml.Class()
        inp = Uml.Parameter(name='x', type=type_)
        ret = bounded(Uml.Parameter, 0, 5, type=type_, direction=Uml.ParameterDirectionKind.return_, isOrdered=True, isUnique=False)
        operation = Uml.Operation(name='f', ownedParameter=[inp, ret])
        owner = Uml.Class(ownedOperation=[operation])
        self.assertEqual(operation.inputParameters(), [inp])
        self.assertEqual(operation.outputParameters(), [ret])
        self.assertEqual(operation.returnResult(), [ret])
        self.assertEqual((operation.lower, operation.upper, operation.type, operation.isOrdered, operation.isUnique), (0, 5, type_, True, False))
        other = Uml.Operation(name='f', ownedParameter=[Uml.Parameter(name='x', type=type_), bounded(Uml.Parameter, 0, 5, type=type_, direction=ret.direction, isOrdered=True, isUnique=False)])
        owner.ownedOperation.append(other)
        self.assertFalse(operation.isDistinguishableFrom(other, owner))
        other.ownedParameter[0].name = 'y'
        self.assertTrue(operation.isDistinguishableFrom(other, owner))
        self.assertTrue(check(operation, 'Operation.at_most_one_return'))
        operation.ownedParameter.append(Uml.Parameter(direction=ret.direction))
        self.assertFalse(check(operation, 'Operation.at_most_one_return'))
        operation.bodyCondition = Uml.Constraint()
        self.assertFalse(check(operation, 'Operation.only_body_for_query'))
        operation.isQuery = True
        self.assertTrue(check(operation, 'Operation.only_body_for_query'))
        operation.isAbstract = True
        operation.method.append(Uml.OpaqueBehavior())
        self.assertFalse(check(operation, 'BehavioralFeature.abstract_no_method'))
        empty = Uml.Operation()
        self.assertEqual((empty.lower, empty.upper, empty.type, empty.isOrdered, empty.isUnique), (None, None, None, False, True))

    @verifies('Operation.isConsistentWith', 'Operation-isConsistentWith-pre')
    def test_operation_redefinition_input_output_and_inout_multiplicities(self):
        base, child, type_ = Uml.Class(), Uml.Class(), Uml.Class()
        child.generalization.append(Uml.Generalization(general=base))
        original, replacement = Uml.Operation(), Uml.Operation()
        base.ownedOperation.append(original)
        child.ownedOperation.append(replacement)
        a, b = bounded(Uml.Parameter, 1, 2, type=type_), bounded(Uml.Parameter, 0, 3, type=type_)
        original.ownedParameter.append(a)
        replacement.ownedParameter.append(b)
        self.assertTrue(original.isConsistentWith(replacement))
        a.direction = b.direction = Uml.ParameterDirectionKind.out
        self.assertFalse(original.isConsistentWith(replacement))
        b.lowerValue.value, b.upperValue.value = 1, 1
        self.assertTrue(original.isConsistentWith(replacement))
        a.direction = b.direction = Uml.ParameterDirectionKind.inout
        self.assertFalse(original.isConsistentWith(replacement))
        b.upperValue.value = 2
        self.assertTrue(original.isConsistentWith(replacement))
        b.isUnique = False
        self.assertFalse(original.isConsistentWith(replacement))
        child.generalization.clear()
        with self.assertRaises(ValueError): original.isConsistentWith(replacement)

    @verifies('Parameter.default', 'Parameter.in_and_out', 'Parameter.not_exception', 'Parameter.stream_and_exception',
              'Parameter.object_effect', 'Parameter.reentrant_behaviors', 'Parameter.connector_end')
    def test_parameter_defaults_effects_streaming_and_connector_context(self):
        param = Uml.Parameter(type=Uml.PrimitiveType(name='String'), defaultValue=Uml.LiteralString(value='default'))
        self.assertEqual(param.default, 'default')
        param.type = Uml.PrimitiveType(name='Integer')
        self.assertIsNone(param.default)
        param.effect = Uml.ParameterEffectKind.create
        self.assertFalse(check(param, 'Parameter.in_and_out'))
        param.direction = Uml.ParameterDirectionKind.out
        self.assertTrue(check(param, 'Parameter.in_and_out'))
        self.assertFalse(check(param, 'Parameter.object_effect'))
        param.effect = None
        self.assertTrue(check(param, 'Parameter.object_effect'))
        param.isException = True
        self.assertTrue(check(param, 'Parameter.not_exception'))
        param.direction = Uml.ParameterDirectionKind.in_
        self.assertFalse(check(param, 'Parameter.not_exception'))
        param.isStream = True
        self.assertFalse(check(param, 'Parameter.stream_and_exception'))
        behavior = Uml.OpaqueBehavior(ownedParameter=[param], isReentrant=True)
        self.assertFalse(check(param, 'Parameter.reentrant_behaviors'))
        behavior.isReentrant = False
        self.assertTrue(check(param, 'Parameter.reentrant_behaviors'))
        end = Uml.ConnectorEnd(role=param)
        self.assertFalse(check(param, 'Parameter.connector_end'))
        collaboration = Uml.Collaboration(collaborationRole=[param])
        self.assertTrue(check(param, 'Parameter.connector_end'))

    @verifies('ParameterSet.same_parameterized_entity', 'ParameterSet.input', 'ParameterSet.two_parameter_sets')
    def test_parameter_sets_same_owner_direction_streaming_and_distinct_alternatives(self):
        a, b, extra = Uml.Parameter(), Uml.Parameter(), Uml.Parameter()
        one, two = Uml.ParameterSet(parameter=[a]), Uml.ParameterSet(parameter=[b])
        operation = Uml.Operation(ownedParameter=[a, b, extra], ownedParameterSet=[one, two])
        self.assertTrue(check(one, 'ParameterSet.same_parameterized_entity'))
        self.assertFalse(check(one, 'ParameterSet.input'))
        extra.isStream = True
        self.assertTrue(check(one, 'ParameterSet.input'))
        self.assertTrue(check(one, 'ParameterSet.two_parameter_sets'))
        two.parameter = [a]
        self.assertFalse(check(one, 'ParameterSet.two_parameter_sets'))
        one.parameter.append(b)
        b.direction = Uml.ParameterDirectionKind.out
        self.assertFalse(check(one, 'ParameterSet.same_parameterized_entity'))

    @verifies('OperationTemplateParameter.match_default_signature', 'RedefinableTemplateSignature.inheritedParameter',
              'RedefinableTemplateSignature.isConsistentWith', 'RedefinableTemplateSignature.redefines_parents', 'RedefinableTemplateSignature-isConsistentWith-pre')
    def test_template_defaults_and_inherited_signatures(self):
        type_ = Uml.Class()
        formal = Uml.Operation(ownedParameter=[Uml.Parameter(type=type_)])
        default = Uml.Operation(ownedParameter=[Uml.Parameter(type=type_)])
        parameter = Uml.OperationTemplateParameter(parameteredElement=formal, default=default)
        self.assertTrue(check(parameter, 'OperationTemplateParameter.match_default_signature'))
        default.ownedParameter[0].isOrdered = True
        self.assertFalse(check(parameter, 'OperationTemplateParameter.match_default_signature'))
        base, child = Uml.Class(), Uml.Class()
        child.generalization.append(Uml.Generalization(general=base))
        parent = Uml.RedefinableTemplateSignature(ownedParameter=[parameter])
        current = Uml.RedefinableTemplateSignature()
        base.ownedTemplateSignature, child.ownedTemplateSignature = parent, current
        self.assertFalse(check(current, 'RedefinableTemplateSignature.redefines_parents'))
        current.extendedSignature.append(parent)
        self.assertTrue(check(current, 'RedefinableTemplateSignature.redefines_parents'))
        self.assertEqual(list(current.inheritedParameter), [parameter])
        self.assertTrue(parent.isConsistentWith(current))
        child.generalization.clear()
        with self.assertRaises(ValueError): parent.isConsistentWith(current)
