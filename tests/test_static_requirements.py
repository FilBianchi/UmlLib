"""Independent negative cases for prose requirements absent from XMI predicates."""
import unittest
import Uml
from umltools import ModelSession
from umltools.native import check, NativeNotImplemented
from umltools.static_requirements import check_static, deployed_elements
from semantic_cases import verifies


class StaticRequirementCases(unittest.TestCase):
    def setUp(self):
        self.session = ModelSession()
        self.session.__enter__()
        self.base = Uml.Class()
        self.child = Uml.Class(generalization=[Uml.Generalization(general=self.base)])

    def tearDown(self): self.session.__exit__(None, None, None)

    def behavior(self, inputs, outputs):
        return Uml.OpaqueBehavior(ownedParameter=[Uml.Parameter(type=t) for t in inputs] +
             [Uml.Parameter(type=t, direction=Uml.ParameterDirectionKind.return_) for t in outputs])

    @verifies('prose:ObjectFlow.selection_types')
    def test_selection_input_contravariance_output_covariance_and_validation(self):
        source = Uml.CentralBufferNode(type=self.base)
        flow = Uml.ObjectFlow(source=source, target=Uml.CentralBufferNode(), selection=self.behavior([self.base], [self.child]))
        rule = 'prose:ObjectFlow.selection_types'
        self.assertTrue(check_static(flow, rule))
        flow.selection.ownedParameter[0].type = self.child
        self.assertFalse(check_static(flow, rule))
        self.assertIn(('constraint', rule), flow.validate())
        flow.selection.ownedParameter[0].type = self.base
        flow.selection.ownedParameter[1].type = Uml.Class()
        self.assertFalse(check_static(flow, rule))
        source.type = None
        with self.assertRaises(NativeNotImplemented): check_static(flow, rule)
        self.assertIn(('unsupported constraint', rule), flow.validate())

    @verifies('prose:ObjectFlow.transformation_types')
    def test_transformation_path_types_through_cycles_and_downstream_adapters(self):
        source = Uml.CentralBufferNode(type=self.child)
        merge = Uml.MergeNode()
        flow = Uml.ObjectFlow(source=source, target=merge, transformation=self.behavior([self.base], [self.child]))
        Uml.ObjectFlow(source=merge, target=merge)
        target = Uml.CentralBufferNode(type=self.base)
        downstream = Uml.ObjectFlow(source=merge, target=target)
        rule = 'prose:ObjectFlow.transformation_types'
        self.assertTrue(check_static(flow, rule))
        target.type = Uml.Class()
        self.assertFalse(check_static(flow, rule))
        # A downstream transformer accepts the preceding transformed tokens and
        # emits a different type. Comparing directly to the final node would be wrong.
        downstream.transformation = self.behavior([self.base], [target.type])
        self.assertTrue(check_static(flow, rule))
        flow.transformation.ownedParameter[0].type = Uml.Class()
        self.assertFalse(check_static(flow, rule))

    @verifies('prose:DecisionNode.input_types')
    def test_two_decision_inputs_have_distinct_corresponding_types(self):
        other = Uml.Class()
        node = Uml.DecisionNode(decisionInput=self.behavior([self.base, other], []))
        regular = Uml.ObjectFlow(source=Uml.CentralBufferNode(type=self.child), target=node)
        decision = Uml.ObjectFlow(source=Uml.CentralBufferNode(type=other), target=node)
        node.decisionInputFlow = decision
        rule = 'prose:DecisionNode.input_types'
        self.assertTrue(check_static(node, rule))
        node.decisionInput.ownedParameter.reverse()
        self.assertFalse(check_static(node, rule))
        self.assertIn(('constraint', rule), node.validate())
        node.decisionInput.ownedParameter.reverse()
        regular.source.type = None
        with self.assertRaises(NativeNotImplemented): check_static(node, rule)

    @verifies('prose:DecisionNode.input_types')
    def test_decision_control_object_and_optional_input_modes(self):
        rule = 'prose:DecisionNode.input_types'
        node = Uml.DecisionNode(decisionInput=self.behavior([], []))
        regular = Uml.ControlFlow(source=Uml.InitialNode(), target=node)
        self.assertTrue(check_static(node, rule))
        decision = Uml.ObjectFlow(source=Uml.CentralBufferNode(type=self.child), target=node)
        node.decisionInputFlow = decision
        self.assertFalse(check_static(node, rule))
        node.decisionInput.ownedParameter.append(Uml.Parameter(type=self.base))
        self.assertTrue(check_static(node, rule))
        regular.delete()
        node.decisionInputFlow = None
        self.assertTrue(check_static(node, rule))
        node.decisionInput.ownedParameter[0].type = Uml.Class()
        self.assertFalse(check_static(node, rule))
        node.decisionInput.ownedParameter[0].type = self.base
        another = Uml.ObjectFlow(source=Uml.CentralBufferNode(type=self.child), target=node)
        self.assertTrue(check_static(node, rule))
        another.source.type = Uml.Class()
        self.assertFalse(check_static(node, rule))

    @verifies('prose:Message.reply_argument_types')
    def test_direct_reply_values_wildcards_expression_operands_and_parameter_directions(self):
        op = Uml.Operation(ownedParameter=[Uml.Parameter(type=self.base),
                Uml.Parameter(type=self.base, direction=Uml.ParameterDirectionKind.inout),
                Uml.Parameter(type=self.base, direction=Uml.ParameterDirectionKind.return_)])
        literal = Uml.LiteralInteger(type=Uml.Class())
        message = Uml.Message(signature=op, messageSort=Uml.MessageSort.reply, argument=[literal, Uml.Expression()])
        rule = 'prose:Message.reply_argument_types'
        self.assertTrue(check(message, 'Message.signature_is_operation_reply'))  # Reference body is intentionally preserved.
        self.assertFalse(check_static(message, rule))
        self.assertIn(('constraint', rule), message.validate())
        literal.type = self.child
        self.assertTrue(check_static(message, rule))
        message.argument[1] = Uml.Expression(operand=[Uml.LiteralInteger(type=Uml.Class())])
        self.assertFalse(check_static(message, rule))
        message.argument.clear()
        self.assertFalse(check_static(message, rule))

    @verifies('prose:DeploymentTarget.resolved_elements', 'prose:DeploymentSpecification.configured_instance_elements')
    def test_artifact_instance_manifestations_union_and_configuration_cannot_pass_vacuously(self):
        component, wrong = Uml.Component(), Uml.Class()
        first = Uml.Artifact(manifestation=[Uml.Manifestation(utilizedElement=component)])
        second = Uml.Artifact(manifestation=[Uml.Manifestation(utilizedElement=wrong)])
        instance = Uml.InstanceSpecification(classifier=[first, second])
        config = Uml.DeploymentSpecification()
        target = Uml.ExecutionEnvironment(deployment=[Uml.Deployment(deployedArtifact=[instance, first], configuration=[config])])
        self.assertEqual(target.deployedElement, [component])
        self.assertEqual(set(deployed_elements(target)), {component, wrong})
        rule = 'prose:DeploymentSpecification.configured_instance_elements'
        self.assertFalse(check_static(config, rule))
        self.assertIn(('constraint', rule), config.validate())
        second.manifestation[0].utilizedElement = component
        self.assertEqual(deployed_elements(target), [component])
        self.assertTrue(check_static(config, rule))
        second.delete()
        self.assertEqual(deployed_elements(target), [component])
        first.delete()
        with self.assertRaises(ValueError): deployed_elements(target)
        self.assertIn(('invalid constraint', rule), config.validate())
