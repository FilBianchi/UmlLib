"""Activity graphs, boundary crossings and represented numeric evidence."""
import unittest
import Uml
from umltools import ModelSession
from umltools.native import check, NativeNotImplemented
from umltools.expression_semantics import register_expression_facts
from semantic_cases import verifies


def bounded(cls, lower=1, upper=1, **kwargs):
    return cls(lowerValue=Uml.LiteralInteger(value=lower), upperValue=Uml.LiteralUnlimitedNatural(value=upper), **kwargs)


class ActivityCases(unittest.TestCase):
    def setUp(self):
        self.session = ModelSession()
        self.session.__enter__()

    def tearDown(self): self.session.__exit__(None, None, None)

    def rules(self, node, *names, expected=True):
        for name in names:
            with self.subTest(rule=name): self.assertEqual(check(node, name), expected)

    @verifies('Activity.maximum_one_parameter_node', 'Activity.maximum_two_parameter_nodes',
              'ActivityParameterNode.has_parameters', 'ActivityParameterNode.same_type',
              'ActivityParameterNode.no_incoming_edges', 'ActivityParameterNode.no_outgoing_edges', 'ActivityParameterNode.no_edges')
    def test_parameter_nodes_counts_directions_types_and_edge_roles(self):
        t = Uml.Class()
        p = Uml.Parameter(type=t)
        a = Uml.Activity(ownedParameter=[p])
        self.rules(a, 'Activity.maximum_one_parameter_node', expected=False)
        n = Uml.ActivityParameterNode(parameter=p, type=t)
        a.node.append(n)
        self.rules(a, 'Activity.maximum_one_parameter_node')
        self.rules(n, 'ActivityParameterNode.has_parameters', 'ActivityParameterNode.same_type',
                   'ActivityParameterNode.no_incoming_edges', 'ActivityParameterNode.no_outgoing_edges', 'ActivityParameterNode.no_edges')
        edge = Uml.ObjectFlow(source=n, target=Uml.CentralBufferNode())
        self.rules(n, 'ActivityParameterNode.no_incoming_edges')
        p.direction = Uml.ParameterDirectionKind.out
        self.rules(n, 'ActivityParameterNode.no_incoming_edges', expected=False)
        edge.source, edge.target = edge.target, n
        self.rules(n, 'ActivityParameterNode.no_outgoing_edges')
        p.direction = Uml.ParameterDirectionKind.in_
        self.rules(n, 'ActivityParameterNode.no_outgoing_edges', expected=False)
        Uml.ObjectFlow(source=n, target=Uml.CentralBufferNode())
        self.rules(n, 'ActivityParameterNode.no_edges', expected=False)
        n.type = Uml.Class()
        self.rules(n, 'ActivityParameterNode.same_type', expected=False)
        p.direction = Uml.ParameterDirectionKind.inout
        self.rules(a, 'Activity.maximum_two_parameter_nodes', expected=False)
        second = Uml.ActivityParameterNode(parameter=p)
        a.node.append(second)
        self.rules(a, 'Activity.maximum_two_parameter_nodes')
        Uml.ObjectFlow(source=Uml.CentralBufferNode(), target=second)
        self.rules(a, 'Activity.maximum_two_parameter_nodes', expected=False)
        n.parameter = Uml.Parameter()
        self.rules(n, 'ActivityParameterNode.has_parameters', expected=False)

    @verifies('ActivityEdge.source_and_target', 'ActivityNode.containingActivity', 'ActivityEdge.isConsistentWith',
              'ActivityNode.isConsistentWith', 'ActivityGroup.containingActivity', 'ActivityGroup.nodes_and_edges',
              'ActivityGroup.not_contained', 'ActivityGroup-containedNode', 'ActivityGroup-containedEdge',
              'ActivityGroup-subgroup', 'ActivityGroup-superGroup', 'ActivityNode-inGroup', 'ActivityEdge-inGroup')
    def test_partition_unions_nested_ownership_and_foreign_edge_endpoints(self):
        a, other = Uml.Activity(), Uml.Activity()
        outer, inner = Uml.ActivityPartition(), Uml.ActivityPartition()
        outer.subpartition.append(inner)
        a.partition.append(outer)
        n, end = Uml.OpaqueAction(), Uml.OpaqueAction()
        a.node.extend([n, end])
        edge = Uml.ControlFlow(source=n, target=end)
        a.edge.append(edge)
        inner.node.append(n)
        inner.edge.append(edge)
        self.assertIs(inner.containingActivity(), a)
        self.assertIs(n.containingActivity(), a)
        self.assertEqual(inner.containedNode, [n])
        self.assertEqual(inner.containedEdge, [edge])
        self.assertEqual(outer.subgroup, [inner])
        self.assertIs(inner.superGroup, outer)
        self.assertEqual(n.inGroup, [inner])
        self.assertEqual(edge.inGroup, [inner])
        self.rules(edge, 'ActivityEdge.source_and_target')
        self.rules(inner, 'ActivityGroup.nodes_and_edges', 'ActivityGroup.not_contained')
        outer.node.append(n)
        self.rules(inner, 'ActivityGroup.not_contained', expected=False)
        outer.node.remove(n)
        foreign = Uml.OpaqueAction()
        other.node.append(foreign)
        edge.target = foreign
        self.rules(edge, 'ActivityEdge.source_and_target', expected=False)
        self.assertTrue(n.isConsistentWith(foreign))
        self.assertFalse(n.isConsistentWith(edge))
        self.assertTrue(edge.isConsistentWith(Uml.ObjectFlow()))
        self.assertFalse(edge.isConsistentWith(n))

    @verifies('ActivityPartition.represents_classifier', 'ActivityPartition.represents_property',
              'ActivityPartition.represents_property_and_is_contained', 'ActivityPartition.dimension_not_contained')
    def test_partition_classifier_property_and_external_siblings(self):
        classifier, nested = Uml.Class(), Uml.Class()
        classifier.nestedClassifier.append(nested)
        parent = Uml.ActivityPartition(represents=classifier)
        child = Uml.ActivityPartition(represents=nested)
        parent.subpartition.append(child)
        self.rules(child, 'ActivityPartition.represents_classifier')
        child.represents = Uml.Class()
        self.rules(child, 'ActivityPartition.represents_classifier', expected=False)
        child.isExternal = True
        self.rules(child, 'ActivityPartition.represents_classifier')
        child.isDimension = True
        self.rules(child, 'ActivityPartition.dimension_not_contained', expected=False)
        child.isDimension = False
        self.rules(child, 'ActivityPartition.dimension_not_contained')
        prop = Uml.Property()
        classifier.ownedAttribute.append(prop)
        child.represents, child.isExternal = prop, False
        self.rules(child, 'ActivityPartition.represents_property_and_is_contained', 'ActivityPartition.represents_property')
        sibling = Uml.ActivityPartition(represents=nested)
        parent.subpartition.append(sibling)
        self.rules(child, 'ActivityPartition.represents_property', expected=False)
        sibling.isExternal = True
        self.rules(child, 'ActivityPartition.represents_property')
        child.represents = Uml.Property()
        self.rules(child, 'ActivityPartition.represents_property_and_is_contained', expected=False)

    @verifies('InitialNode.no_incoming_edges', 'InitialNode.control_edges', 'FinalNode.no_outgoing_edges',
              'ForkNode.edges', 'ForkNode.one_incoming_edge', 'MergeNode.edges', 'MergeNode.one_outgoing_edge',
              'JoinNode.one_outgoing_edge', 'JoinNode.incoming_object_flow', 'ControlFlow.object_nodes')
    def test_control_graph_and_mixed_object_flows(self):
        initial, fork, merge, join, final = Uml.InitialNode(), Uml.ForkNode(), Uml.MergeNode(), Uml.JoinNode(), Uml.ActivityFinalNode()
        Uml.ControlFlow(source=initial, target=fork)
        Uml.ControlFlow(source=fork, target=merge)
        Uml.ControlFlow(source=merge, target=join)
        Uml.ControlFlow(source=join, target=final)
        for node, names in ((initial, ('InitialNode.no_incoming_edges','InitialNode.control_edges')),
                            (fork, ('ForkNode.edges','ForkNode.one_incoming_edge')),
                            (merge, ('MergeNode.edges','MergeNode.one_outgoing_edge')),
                            (join, ('JoinNode.one_outgoing_edge','JoinNode.incoming_object_flow')),
                            (final, ('FinalNode.no_outgoing_edges',))): self.rules(node, *names)
        object_ = Uml.CentralBufferNode()
        edge = Uml.ControlFlow(source=object_, target=initial)
        self.rules(edge, 'ControlFlow.object_nodes', expected=False)
        object_.isControlType = True
        self.rules(edge, 'ControlFlow.object_nodes')
        self.rules(initial, 'InitialNode.no_incoming_edges', expected=False)
        Uml.ObjectFlow(source=initial, target=fork)
        self.rules(initial, 'InitialNode.control_edges', expected=False)
        self.rules(fork, 'ForkNode.edges', 'ForkNode.one_incoming_edge', expected=False)
        Uml.ObjectFlow(source=fork, target=merge)
        self.rules(merge, 'MergeNode.edges', expected=False)
        Uml.ObjectFlow(source=merge, target=join)
        self.rules(merge, 'MergeNode.one_outgoing_edge', expected=False)
        self.rules(join, 'JoinNode.incoming_object_flow', expected=False)
        Uml.ControlFlow(source=final, target=join)
        self.rules(final, 'FinalNode.no_outgoing_edges', expected=False)
        Uml.ControlFlow(source=join, target=final)
        self.rules(join, 'JoinNode.one_outgoing_edge', expected=False)

    @verifies('DecisionNode.zero_input_parameters', 'DecisionNode.edges', 'DecisionNode.decision_input_flow_incoming',
              'DecisionNode.two_input_parameters', 'DecisionNode.incoming_outgoing_edges',
              'DecisionNode.incoming_control_one_input_parameter', 'DecisionNode.parameters',
              'DecisionNode.incoming_object_one_input_parameter')
    def test_decision_input_modes_and_return_direction(self):
        behavior = Uml.OpaqueBehavior(ownedParameter=[Uml.Parameter(direction=Uml.ParameterDirectionKind.return_)])
        decision = Uml.DecisionNode(decisionInput=behavior)
        self.rules(decision, 'DecisionNode.incoming_outgoing_edges', expected=False)
        control = Uml.ControlFlow(source=Uml.InitialNode(), target=decision)
        outgoing = Uml.ControlFlow(source=decision, target=Uml.ActivityFinalNode())
        self.rules(decision, 'DecisionNode.zero_input_parameters', 'DecisionNode.parameters',
                   'DecisionNode.edges', 'DecisionNode.incoming_outgoing_edges', 'DecisionNode.decision_input_flow_incoming')
        parameter = Uml.Parameter()
        behavior.ownedParameter.append(parameter)
        self.rules(decision, 'DecisionNode.zero_input_parameters', expected=False)
        data = Uml.ObjectFlow(source=Uml.CentralBufferNode(), target=decision)
        decision.decisionInputFlow = data
        self.rules(decision, 'DecisionNode.edges', 'DecisionNode.decision_input_flow_incoming', 'DecisionNode.incoming_control_one_input_parameter')
        behavior.ownedParameter.append(Uml.Parameter())
        self.rules(decision, 'DecisionNode.incoming_control_one_input_parameter', expected=False)
        control.delete()
        outgoing.delete()
        Uml.ObjectFlow(source=decision, target=Uml.CentralBufferNode())
        regular = Uml.ObjectFlow(source=Uml.CentralBufferNode(), target=decision)
        self.rules(decision, 'DecisionNode.two_input_parameters', 'DecisionNode.edges')
        behavior.ownedParameter.pop()
        self.rules(decision, 'DecisionNode.two_input_parameters', expected=False)
        decision.decisionInputFlow = None
        data.delete()
        self.rules(decision, 'DecisionNode.incoming_object_one_input_parameter')
        behavior.ownedParameter.clear()
        self.rules(decision, 'DecisionNode.incoming_object_one_input_parameter', 'DecisionNode.parameters', expected=False)
        decision.decisionInputFlow = Uml.ObjectFlow()
        self.rules(decision, 'DecisionNode.decision_input_flow_incoming', expected=False)

    @verifies('ExceptionHandler.handler_body_edges', 'ExceptionHandler.output_pins', 'ExceptionHandler.one_input',
              'ExceptionHandler.edge_source_target', 'ExceptionHandler.handler_body_owner', 'ExceptionHandler.exception_input_type')
    def test_exception_handler_pin_compatibility_and_closed_boundary(self):
        t = Uml.Class()
        protected = Uml.OpaqueAction(outputValue=[bounded(Uml.OutputPin, type=t)])
        pin = bounded(Uml.InputPin, type=t)
        handler = Uml.OpaqueAction(inputValue=[pin], outputValue=[bounded(Uml.OutputPin, type=t)])
        a = Uml.Activity(node=[protected, handler])
        h = Uml.ExceptionHandler(protectedNode=protected, handlerBody=handler, exceptionInput=pin, exceptionType=[t])
        self.rules(h, 'ExceptionHandler.handler_body_edges', 'ExceptionHandler.output_pins', 'ExceptionHandler.one_input',
                   'ExceptionHandler.edge_source_target', 'ExceptionHandler.handler_body_owner', 'ExceptionHandler.exception_input_type')
        handler.outputValue[0].type = Uml.Class()
        self.rules(h, 'ExceptionHandler.output_pins', expected=False)
        handler.inputValue.append(bounded(Uml.InputPin))
        self.rules(h, 'ExceptionHandler.one_input', expected=False)
        Uml.ObjectFlow(source=handler.outputValue[0], target=Uml.CentralBufferNode())
        self.rules(h, 'ExceptionHandler.edge_source_target', expected=False)
        Uml.ControlFlow(source=protected, target=handler)
        self.rules(h, 'ExceptionHandler.handler_body_edges', expected=False)
        h.exceptionType = [Uml.Class()]
        self.rules(h, 'ExceptionHandler.exception_input_type', expected=False)
        a.node.remove(handler)
        self.rules(h, 'ExceptionHandler.handler_body_owner', expected=False)

    @verifies('InterruptibleActivityRegion.interrupting_edges')
    def test_interrupting_edge_exits_region_but_not_activity(self):
        inside, outside = Uml.OpaqueAction(), Uml.OpaqueAction()
        region = Uml.InterruptibleActivityRegion(node=[inside])
        activity = Uml.Activity(node=[inside, outside], group=[region])
        edge = Uml.ControlFlow(source=inside, target=outside)
        region.interruptingEdge.append(edge)
        self.rules(region, 'InterruptibleActivityRegion.interrupting_edges')
        region.node.append(outside)
        self.rules(region, 'InterruptibleActivityRegion.interrupting_edges', expected=False)
        region.node.remove(outside)
        activity.node.remove(outside)
        self.rules(region, 'InterruptibleActivityRegion.interrupting_edges', expected=False)

    @verifies('ObjectFlow.compatible_types', 'ObjectFlow.same_upper_bounds', 'ObjectFlow.target',
              'ObjectFlow.no_executable_nodes', 'ObjectFlow.is_multicast_or_is_multireceive')
    def test_flow_paths_cycles_bounds_and_unknown_constant_evidence(self):
        base = Uml.Class()
        child = Uml.Class(generalization=[Uml.Generalization(general=base)])
        source = Uml.CentralBufferNode(type=child, upperBound=Uml.LiteralUnlimitedNatural(value=4))
        target = Uml.CentralBufferNode(type=base, upperBound=Uml.LiteralUnlimitedNatural(value=4))
        merge = Uml.MergeNode()
        flow = Uml.ObjectFlow(source=source, target=merge, weight=Uml.LiteralInteger(value=4))
        Uml.ObjectFlow(source=merge, target=merge)
        Uml.ObjectFlow(source=merge, target=target)
        self.rules(flow, 'ObjectFlow.compatible_types', 'ObjectFlow.same_upper_bounds', 'ObjectFlow.target',
                   'ObjectFlow.no_executable_nodes', 'ObjectFlow.is_multicast_or_is_multireceive')
        target.type = Uml.Class()
        self.rules(flow, 'ObjectFlow.compatible_types', expected=False)
        target.upperBound.value = 3
        self.rules(flow, 'ObjectFlow.same_upper_bounds', 'ObjectFlow.target', expected=False)
        flow.isMulticast = flow.isMultireceive = True
        self.rules(flow, 'ObjectFlow.is_multicast_or_is_multireceive', expected=False)
        opaque = Uml.OpaqueExpression(body=['capacity'], language=['custom'])
        source.upperBound = target.upperBound = None
        # Composite expressions have separate owners even if they denote the same text.
        source.upperBound = opaque
        target.upperBound = Uml.OpaqueExpression(body=['capacity'], language=['custom'])
        with self.assertRaises(NativeNotImplemented): check(flow, 'ObjectFlow.same_upper_bounds')
        flow.weight = Uml.OpaqueExpression(body=['weight'], language=['custom'])
        with self.assertRaises(NativeNotImplemented): check(flow, 'ObjectFlow.target')
        register_expression_facts(flow.weight, constant=False)
        self.rules(flow, 'ObjectFlow.target')
        register_expression_facts(flow.weight, constant=True)
        with self.assertRaises(NativeNotImplemented): check(flow, 'ObjectFlow.target')
        self.assertIn(('unsupported constraint', 'ObjectFlow.target'), flow.validate())
        flow.source = Uml.OpaqueAction()
        self.rules(flow, 'ObjectFlow.no_executable_nodes', expected=False)

    @verifies('ObjectNode.input_output_parameter', 'ObjectNode.selection_behavior', 'ObjectNode.object_flow_edges',
              'ObjectFlow.input_and_output_parameter', 'ObjectFlow.transformation_behavior', 'ObjectFlow.selection_behavior')
    def test_selection_variance_multiplicities_and_transformation_signature(self):
        base = Uml.Class()
        child = Uml.Class(generalization=[Uml.Generalization(general=base)])
        behavior = Uml.OpaqueBehavior(ownedParameter=[bounded(Uml.Parameter, 0, float('inf'), type=base, isUnique=False),
                                                     bounded(Uml.Parameter, type=child, direction=Uml.ParameterDirectionKind.return_)])
        node = Uml.CentralBufferNode(type=base, selection=behavior, ordering=Uml.ObjectNodeOrderingKind.ordered)
        flow = Uml.ObjectFlow(source=node, target=Uml.CentralBufferNode(), selection=behavior, transformation=behavior)
        self.rules(node, 'ObjectNode.input_output_parameter', 'ObjectNode.selection_behavior', 'ObjectNode.object_flow_edges')
        self.rules(flow, 'ObjectFlow.input_and_output_parameter', 'ObjectFlow.transformation_behavior', 'ObjectFlow.selection_behavior')
        behavior.ownedParameter[1].type = Uml.Class()
        self.rules(node, 'ObjectNode.input_output_parameter', expected=False)
        behavior.ownedParameter[0].isUnique = True
        self.rules(flow, 'ObjectFlow.input_and_output_parameter', expected=False)
        behavior.ownedParameter.append(Uml.Parameter())
        self.rules(flow, 'ObjectFlow.transformation_behavior', expected=False)
        node.ordering = Uml.ObjectNodeOrderingKind.unordered
        self.rules(node, 'ObjectNode.selection_behavior', expected=False)
        Uml.ControlFlow(source=node, target=Uml.InitialNode())
        self.rules(node, 'ObjectNode.object_flow_edges', expected=False)
        flow.source = Uml.MergeNode()
        self.rules(flow, 'ObjectFlow.selection_behavior', expected=False)

    @verifies('ObjectFlow.same_upper_bounds', 'ObjectFlow.target')
    def test_wrong_numeric_literal_kinds_are_invalid_not_successful(self):
        source = Uml.CentralBufferNode(upperBound=Uml.LiteralString(value='4'))
        target = Uml.CentralBufferNode(upperBound=Uml.LiteralString(value='4'))
        flow = Uml.ObjectFlow(source=source, target=target, weight=Uml.LiteralInteger(value=1))
        with self.assertRaises(ValueError): check(flow, 'ObjectFlow.same_upper_bounds')
        with self.assertRaises(ValueError): check(flow, 'ObjectFlow.target')
        target.upperBound = Uml.LiteralUnlimitedNatural(value=float('inf'))
        flow.weight = Uml.LiteralString(value='1')
        with self.assertRaises(ValueError): check(flow, 'ObjectFlow.target')
        self.assertIn(('invalid constraint', 'ObjectFlow.target'), flow.validate())
