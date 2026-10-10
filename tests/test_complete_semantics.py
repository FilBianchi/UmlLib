"""Independent model examples for the additional native semantic areas."""
import unittest
from unittest.mock import patch
import Uml
from umltools import ModelSession, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.native import OPERATIONS, CONSTRAINTS, check, instances
from umltools.expression_semantics import register_expression_facts


def bounds(cls, lower=1, upper=1, **values):
    return cls(lowerValue=Uml.LiteralInteger(value=lower), upperValue=Uml.LiteralUnlimitedNatural(value=upper), **values)


class CompleteSemanticsTests(unittest.TestCase):
    def setUp(self):
        self.session = ModelSession()
        self.session.__enter__()

    def tearDown(self): self.session.__exit__(None, None, None)

    def test_every_definition_has_an_explicit_python_implementation(self):
        self.assertEqual(set(OPERATIONS), {f'{s.name}.{n}' for s in SPECIFICATIONS.values() for n in s.operations})
        self.assertEqual(set(CONSTRAINTS), {f'{s.name}.{n}' for s in SPECIFICATIONS.values() for n in s.constraints})

    def test_pin_property_and_operation_with_the_same_name(self):
        pin = bounds(Uml.InputPin, 0, 5)
        object_limit = Uml.LiteralUnlimitedNatural(value=20)
        pin.upperBound = object_limit
        self.assertIs(pin.upperBound, object_limit)
        self.assertEqual(pin.uml_operation('MultiplicityElement', 'upperBound'), 5)
        self.assertTrue(pin.is_(0, 5))
        self.assertTrue(pin.compatibleWith(bounds(Uml.Parameter, 0, 10)))
        self.assertEqual(set(pin.ownedElement), {pin.lowerValue, pin.upperValue, object_limit})

    def test_session_extents_remain_isolated_after_context_exit(self):
        one = Uml.Class()
        with ModelSession(): two = Uml.Class()
        self.assertIn(one, instances(one, 'Class'))
        self.assertNotIn(two, instances(one, 'Class'))
        self.assertEqual(instances(two, 'Class'), [two])

    def test_stored_subset_addition_and_superset_removal(self):
        activity, node = Uml.Activity(), Uml.StructuredActivityNode()
        activity.structuredNode.append(node)
        self.assertIn(node, activity.node)
        self.assertIn(node, activity.group)
        self.assertIs(node.owner, activity)
        self.assertIs(node.containingActivity(), activity)
        self.assertEqual(activity.ownedElement.count(node), 1)
        activity.node.remove(node)
        self.assertNotIn(node, activity.structuredNode)
        self.assertIs(node.owner, activity)  # Still a member of composite Activity::group.
        activity.group.remove(node)
        self.assertIsNone(node.owner)

    def test_template_owned_parameters_subset_parameters(self):
        cls = Uml.Class()
        signature = Uml.RedefinableTemplateSignature()
        parameter = Uml.TemplateParameter(parameteredElement=Uml.Class())
        cls.ownedTemplateSignature = signature
        signature.ownedParameter.append(parameter)
        self.assertIn(parameter, signature.parameter)
        self.assertIs(parameter.signature, signature)

    def test_nested_action_and_variable_scope(self):
        activity = Uml.Activity()
        outer, inner = Uml.StructuredActivityNode(), Uml.StructuredActivityNode()
        action, unrelated = Uml.OpaqueAction(), Uml.OpaqueAction()
        activity.structuredNode.append(outer)
        outer.node.append(inner)
        inner.node.append(action)
        variable = Uml.Variable()
        outer.variable.append(variable)
        self.assertIs(action.containingBehavior(), activity)
        self.assertIs(action.context, activity)
        self.assertIn(action, outer.allActions())
        self.assertIn(action, outer.allOwnedNodes())
        self.assertTrue(variable.isAccessibleBy(action))
        self.assertFalse(variable.isAccessibleBy(unrelated))

    def test_loop_and_conditional_limit_action_output_exposure(self):
        for cls in (Uml.LoopNode, Uml.ConditionalNode):
            with self.subTest(cls=cls):
                node = cls(node=[Uml.OpaqueAction()])
                self.assertEqual(node.allActions(), [node])
                self.assertEqual(len(node.allOwnedNodes()), 1)

    def test_call_parameter_direction_type_and_multiplicity(self):
        type_ = Uml.Class()
        behavior = Uml.OpaqueBehavior()
        inp = bounds(Uml.Parameter, type=type_)
        out = bounds(Uml.Parameter, type=type_, direction=Uml.ParameterDirectionKind.return_)
        behavior.ownedParameter.extend([inp, out])
        action = Uml.CallBehaviorAction(behavior=behavior)
        action.argument.append(bounds(Uml.InputPin, type=type_))
        action.result.append(bounds(Uml.OutputPin, type=type_))
        self.assertEqual(action.inputParameters(), [inp])
        self.assertEqual(action.outputParameters(), [out])
        self.assertTrue(check(action, 'CallAction.argument_pins'))
        self.assertTrue(check(action, 'CallAction.result_pins'))
        action.argument[0].type = Uml.Class()
        self.assertFalse(check(action, 'CallAction.argument_pins'))

    def test_use_case_include_closure_and_cycle(self):
        a, b, c = Uml.UseCase(name='A'), Uml.UseCase(name='B'), Uml.UseCase(name='C')
        a.include.append(Uml.Include(addition=b))
        b.include.append(Uml.Include(addition=c))
        self.assertEqual(a.allIncludedUseCases(), [b, c])
        self.assertTrue(check(a, 'UseCase.cannot_include_self'))
        c.include.append(Uml.Include(addition=a))
        self.assertFalse(check(a, 'UseCase.cannot_include_self'))

    def test_port_conjugation_and_component_interfaces(self):
        interface = Uml.Interface(name='Service')
        port = Uml.Port(type=interface, aggregation=Uml.AggregationKind.composite)
        component = Uml.Component(ownedAttribute=[port])
        self.assertEqual(port.provided, [interface])
        self.assertEqual(port.required, [])
        self.assertIn(interface, component.provided)
        port.isConjugated = True
        self.assertEqual(port.provided, [])
        self.assertEqual(port.required, [interface])
        self.assertIn(interface, component.required)

    def test_connector_end_order_and_inverse_roles(self):
        first, second = Uml.Class(), Uml.Class()
        a, b = Uml.Property(type=first), Uml.Property(type=second)
        association = Uml.Association(ownedEnd=[a, b])
        role_a, role_b = Uml.Property(type=first), Uml.Property(type=second)
        ea, eb = Uml.ConnectorEnd(role=role_a), Uml.ConnectorEnd(role=role_b)
        connector = Uml.Connector(type=association, end=[ea, eb])
        self.assertIs(ea.definingEnd, a)
        self.assertIs(eb.definingEnd, b)
        self.assertEqual(role_a.end, [ea])
        self.assertTrue(check(connector, 'Connector.types'))
        connector.end.reverse()
        self.assertIs(ea.definingEnd, b)
        self.assertFalse(check(connector, 'Connector.types'))

    def test_message_kind_and_end_navigation(self):
        message = Uml.Message()
        self.assertEqual(message.messageKind, Uml.MessageKind.unknown)
        send, receive = Uml.MessageOccurrenceSpecification(), Uml.MessageOccurrenceSpecification()
        message.sendEvent = send
        self.assertEqual(message.messageKind, Uml.MessageKind.lost)
        message.receiveEvent = receive
        self.assertEqual(message.messageKind, Uml.MessageKind.complete)
        self.assertEqual(send.oppositeEnd(), [receive])
        self.assertTrue(send.isSend())
        self.assertTrue(receive.isReceive())
        message.sendEvent = None
        self.assertEqual(message.messageKind, Uml.MessageKind.found)

    def test_gate_inside_outside_context_and_names(self):
        interaction = Uml.Interaction()
        fragment = Uml.CombinedFragment()
        operand = Uml.InteractionOperand()
        inside, outside = Uml.Gate(), Uml.Gate()
        fragment.operand.append(operand)
        fragment.cfragmentGate.extend([inside, outside])
        interaction.fragment.append(fragment)
        inside_event, outside_event = Uml.MessageOccurrenceSpecification(), Uml.MessageOccurrenceSpecification()
        operand.fragment.append(inside_event)
        interaction.fragment.append(outside_event)
        m1 = Uml.Message(name='request', sendEvent=inside, receiveEvent=inside_event)
        m2 = Uml.Message(name='request', sendEvent=outside_event, receiveEvent=outside)
        interaction.message.extend([m1, m2])
        self.assertTrue(inside.isInsideCF())
        self.assertFalse(inside.isOutsideCF())
        self.assertTrue(outside.isOutsideCF())
        self.assertEqual(inside.getName(), 'in_request')
        self.assertEqual(outside.getName(), 'in_request')
        self.assertTrue(inside.matches(outside))
        self.assertIs(inside.getOperand(), operand)
        self.assertEqual(inside.enclosingFragment(), [fragment])
        self.assertEqual(outside.enclosingFragment(), [interaction])
        self.assertTrue(check(inside, 'Gate.inside_cf_matched'))
        m2.name = 'different'
        self.assertFalse(inside.matches(outside))

    def test_formal_gate_without_message_has_a_defined_kind(self):
        gate = Uml.Gate(name='g')
        interaction = Uml.Interaction(formalGate=[gate])
        self.assertTrue(gate.isFormal())
        self.assertFalse(gate.isInsideCF())
        self.assertFalse(gate.isOutsideCF())
        self.assertEqual(gate.enclosingFragment(), [interaction])

    def test_string_expression_concatenation_and_invalid_operand(self):
        expression = Uml.StringExpression(operand=[Uml.LiteralString(value='Hello'), Uml.LiteralString(value=' UML')])
        self.assertEqual(expression.stringValue(), 'Hello UML')
        self.assertTrue(check(expression, 'StringExpression.operands'))
        expression.operand.append(Uml.LiteralInteger(value=2))
        self.assertFalse(check(expression, 'StringExpression.operands'))
        with self.assertRaises(ValueError): expression.stringValue()

    def test_opaque_expressions_require_declared_language_facts(self):
        expression = Uml.OpaqueExpression(type=Uml.PrimitiveType(name='Boolean'), body=['x > 0'], language=['custom'])
        constraint = Uml.Constraint(specification=expression)
        with patch('umltools.ocl.evaluate', side_effect=AssertionError('No runtime OCL')):
            self.assertIn(('unsupported constraint', 'Constraint.no_side_effects'), constraint.validate())
            register_expression_facts(expression, references=(), pure=True, constant=False)
            self.assertTrue(check(constraint, 'Constraint.no_side_effects'))
            self.assertTrue(check(constraint, 'Constraint.boolean_value'))
            register_expression_facts(expression, references=(), pure=False, constant=False)
            self.assertFalse(check(constraint, 'Constraint.no_side_effects'))

    def test_literal_constraint_needs_no_adapter(self):
        constraint = Uml.Constraint(specification=Uml.LiteralBoolean(value=True))
        self.assertTrue(check(constraint, 'Constraint.boolean_value'))
        self.assertTrue(check(constraint, 'Constraint.no_side_effects'))

    def test_object_flow_type_and_bounds_through_control_node(self):
        base, child = Uml.Class(), Uml.Class()
        child.generalization.append(Uml.Generalization(general=base))
        source = Uml.CentralBufferNode(type=child, upperBound=Uml.LiteralUnlimitedNatural(value=4))
        target = Uml.CentralBufferNode(type=base, upperBound=Uml.LiteralUnlimitedNatural(value=4))
        merge = Uml.MergeNode()
        upstream = Uml.ObjectFlow(source=source, target=merge)
        downstream = Uml.ObjectFlow(source=merge, target=target, weight=Uml.LiteralInteger(value=3))
        self.assertTrue(check(upstream, 'ObjectFlow.compatible_types'))
        self.assertTrue(check(downstream, 'ObjectFlow.same_upper_bounds'))
        self.assertTrue(check(downstream, 'ObjectFlow.target'))
        target.upperBound.value = 2
        self.assertFalse(check(downstream, 'ObjectFlow.target'))
        self.assertFalse(check(upstream, 'ObjectFlow.same_upper_bounds'))
        target.type = Uml.Class()
        self.assertFalse(check(upstream, 'ObjectFlow.compatible_types'))

    def test_extension_base_multiplicities(self):
        profile = Uml.Profile(name='P')
        stereotype = Uml.Stereotype(name='Custom')
        profile.packagedElement.append(stereotype)
        metaclass = Uml.Class(name='Class')
        base = bounds(Uml.Property, type=metaclass, name='base_Class')
        end = Uml.ExtensionEnd(type=stereotype, aggregation=Uml.AggregationKind.composite)
        extension = Uml.Extension(ownedEnd=end)
        stereotype.ownedAttribute.append(base)
        extension.memberEnd.append(base)
        self.assertIs(extension.metaclass, metaclass)
        self.assertFalse(extension.isRequired)
        self.assertIs(stereotype.profile, profile)
        self.assertTrue(check(stereotype, 'Stereotype.base_property_multiplicity_single_extension'))
        base.lowerValue.value = 0
        self.assertFalse(check(stereotype, 'Stereotype.base_property_multiplicity_single_extension'))

    def test_enumeration_literal_scalar_classifier(self):
        enumeration = Uml.Enumeration()
        literal = Uml.EnumerationLiteral(name='red')
        enumeration.ownedLiteral.append(literal)
        self.assertIs(literal.classifier, enumeration)

    def test_deployment_manifestations(self):
        component = Uml.Component()
        artifact = Uml.Artifact(manifestation=[Uml.Manifestation(utilizedElement=component)])
        target = Uml.Node(deployment=[Uml.Deployment(deployedArtifact=[artifact])])
        self.assertEqual(target.deployedElement, [component])

    def test_clauses_allow_acyclic_predecessors_and_reject_cycles(self):
        first, second = Uml.Clause(), Uml.Clause()
        second.predecessorClause.append(first)
        node = Uml.ConditionalNode(clause=[first, second])
        self.assertTrue(check(node, 'ConditionalNode.clause_no_predecessor'))
        first.predecessorClause.append(second)
        self.assertFalse(check(node, 'ConditionalNode.clause_no_predecessor'))

    def test_behavioral_feature_signatures_distinguish_overloads(self):
        cls = Uml.Class()
        a, b = Uml.Operation(name='call'), Uml.Operation(name='call')
        cls.ownedOperation.extend([a, b])
        self.assertFalse(a.isDistinguishableFrom(b, cls))
        b.ownedParameter.append(Uml.Parameter(name='argument'))
        self.assertTrue(a.isDistinguishableFrom(b, cls))

    def test_protocol_transition_referred_operations(self):
        operation = Uml.Operation()
        transition = Uml.ProtocolTransition(trigger=[Uml.Trigger(event=Uml.CallEvent(operation=operation))])
        self.assertEqual(transition.referred, [operation])

    def test_transition_and_vertex_redefinition_consistency(self):
        old_region, new_region = Uml.Region(), Uml.Region()
        old_machine = Uml.StateMachines.StateMachine(region=[old_region])
        new_machine = Uml.StateMachines.StateMachine(region=[new_region], generalization=[Uml.Generalization(general=old_machine)])
        new_region.extendedRegion = old_region
        old_source = Uml.State()
        new_source = Uml.State(redefinedVertex=old_source)
        old_region.subvertex.append(old_source)
        new_region.subvertex.append(new_source)
        old_transition = Uml.Transition(source=old_source)
        new_transition = Uml.Transition(source=new_source)
        old_region.transition.append(old_transition)
        new_region.transition.append(new_transition)
        self.assertTrue(old_transition.isConsistentWith(new_transition))
        self.assertTrue(old_source.isConsistentWith(new_source))
        new_source.redefinedVertex = None
        self.assertFalse(old_transition.isConsistentWith(new_transition))

    def test_subset_and_inverse_failure_roll_back_together(self):
        first, second = Uml.Activity(), Uml.Activity()
        node = Uml.StructuredActivityNode()
        first.structuredNode.append(node)
        with self.assertRaises(ValueError): second.structuredNode.append(node)
        self.assertEqual(second.node, [])
        self.assertEqual(second.group, [])
        self.assertEqual(second.structuredNode, [])
        self.assertIs(node.activity, first)
        self.assertIs(node.owner, first)

    def test_duplicate_parameter_sets_are_rejected(self):
        parameter = Uml.Parameter()
        first, second = Uml.ParameterSet(parameter=[parameter]), Uml.ParameterSet(parameter=[parameter])
        self.assertFalse(check(first, 'ParameterSet.two_parameter_sets'))
        second.parameter.append(Uml.Parameter())
        self.assertTrue(check(first, 'ParameterSet.two_parameter_sets'))

    def test_isolated_information_flows_and_instance_extents(self):
        item = Uml.InformationItem(isAbstract=True)
        flow = Uml.InformationFlow(conveyed=[item], informationSource=[Uml.Class()], informationTarget=[Uml.Class()])
        self.assertTrue(check(flow, 'InformationFlow.sources_and_targets_kind'))
        self.assertTrue(check(item, 'InformationItem.not_instantiable'))
        flow.informationSource.append(Uml.LiteralString())
        self.assertFalse(check(flow, 'InformationFlow.sources_and_targets_kind'))


if __name__ == '__main__': unittest.main()
