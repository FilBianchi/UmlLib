import unittest
import Uml
from umltools import ModelSession
from umltools.native import check, NativeNotImplemented
from umltools.interaction_mapping import bind_gate_endpoint
from semantic_cases import verifies


class InformationFlowCases(unittest.TestCase):
    def setUp(self):
        self.scope = ModelSession()
        self.scope.__enter__()
        self.source, self.target = Uml.Class(name='Source'), Uml.Class(name='Target')

    def tearDown(self): self.scope.__exit__(None, None, None)

    def flow(self, **values):
        return Uml.InformationFlow(informationSource=[self.source], informationTarget=[self.target],
                                   conveyed=[Uml.InformationItem(isAbstract=True)], **values)

    @verifies('InformationFlow.must_conform')
    def test_directed_relationship_allows_conformance_and_reverse_realization(self):
        dependency = Uml.Dependency(client=[self.source], supplier=[self.target])
        flow = self.flow(realization=[dependency])
        self.assertTrue(check(flow, 'InformationFlow.must_conform'))
        dependency.client, dependency.supplier = [self.target], [self.source]
        self.assertTrue(check(flow, 'InformationFlow.must_conform'))
        child = Uml.Class(generalization=[Uml.Generalization(general=self.source)])
        flow.informationSource = [child]
        self.assertTrue(check(flow, 'InformationFlow.must_conform'))
        flow.informationSource = [Uml.Class()]
        self.assertFalse(check(flow, 'InformationFlow.must_conform'))

    @verifies('InformationFlow.must_conform')
    def test_every_flow_endpoint_needs_a_channel_endpoint(self):
        dependency = Uml.Dependency(client=[self.source], supplier=[self.target])
        flow = self.flow(realization=[dependency])
        flow.informationSource.append(Uml.Class())
        self.assertFalse(check(flow, 'InformationFlow.must_conform'))
        dependency.client.append(flow.informationSource[-1])
        self.assertTrue(check(flow, 'InformationFlow.must_conform'))
        dependency.supplier.clear()
        self.assertFalse(check(flow, 'InformationFlow.must_conform'))

    @verifies('InformationFlow.must_conform')
    def test_association_channels_accept_parts_typed_by_end_classifiers(self):
        association = Uml.Association(ownedEnd=[Uml.Property(type=self.source), Uml.Property(type=self.target)])
        flow = self.flow(realization=[association])
        flow.informationSource = [Uml.Property(type=self.source)]
        flow.informationTarget = [Uml.Property(type=self.target)]
        self.assertTrue(check(flow, 'InformationFlow.must_conform'))
        flow.informationTarget[0].type = Uml.Class()
        self.assertFalse(check(flow, 'InformationFlow.must_conform'))

    @verifies('InformationFlow.must_conform')
    def test_connector_needs_distinct_ends_and_exact_part_references(self):
        a, b = Uml.Property(type=self.source), Uml.Property(type=self.target)
        connector = Uml.Connector(end=[Uml.ConnectorEnd(role=a), Uml.ConnectorEnd(role=b)])
        flow = self.flow(realizingConnector=[connector])
        flow.informationSource, flow.informationTarget = [a], [b]
        self.assertTrue(check(flow, 'InformationFlow.must_conform'))
        flow.informationSource = [Uml.Property(type=self.source)]
        self.assertFalse(check(flow, 'InformationFlow.must_conform'))
        flow.informationSource = [a]
        connector.end.pop()
        self.assertFalse(check(flow, 'InformationFlow.must_conform'))

    @verifies('InformationFlow.must_conform')
    def test_connector_port_on_part_is_a_channel_for_that_part(self):
        a, b = Uml.Property(type=self.source), Uml.Property(type=self.target)
        connector = Uml.Connector(end=[Uml.ConnectorEnd(role=Uml.Port(), partWithPort=a), Uml.ConnectorEnd(role=b)])
        flow = self.flow(realizingConnector=[connector])
        flow.informationSource, flow.informationTarget = [a], [b]
        self.assertTrue(check(flow, 'InformationFlow.must_conform'))
        connector.end[0].partWithPort = None
        self.assertFalse(check(flow, 'InformationFlow.must_conform'))

    @verifies('InformationFlow.must_conform')
    def test_nary_association_can_realize_multiple_source_participants(self):
        third = Uml.Class()
        association = Uml.Association(ownedEnd=[Uml.Property(type=self.source), Uml.Property(type=third), Uml.Property(type=self.target)])
        flow = self.flow(realization=[association])
        flow.informationSource.append(third)
        self.assertTrue(check(flow, 'InformationFlow.must_conform'))
        flow.informationTarget.append(third)
        self.assertFalse(check(flow, 'InformationFlow.must_conform'))

    @verifies('InformationFlow.must_conform')
    def test_reflexive_association_uses_two_distinct_ends_of_the_same_type(self):
        association = Uml.Association(ownedEnd=[Uml.Property(type=self.source), Uml.Property(type=self.source)])
        flow = self.flow(realization=[association])
        flow.informationTarget = [self.source]
        self.assertTrue(check(flow, 'InformationFlow.must_conform'))
        association.memberEnd.pop()
        self.assertFalse(check(flow, 'InformationFlow.must_conform'))

    @verifies('InformationFlow.must_conform')
    def test_activity_edge_preserves_its_direction(self):
        a, b = Uml.InitialNode(), Uml.ActivityFinalNode()
        edge = Uml.ControlFlow(source=a, target=b)
        flow = self.flow(realizingActivityEdge=[edge])
        flow.informationSource, flow.informationTarget = [a], [b]
        self.assertTrue(check(flow, 'InformationFlow.must_conform'))
        flow.informationSource, flow.informationTarget = [b], [a]
        self.assertFalse(check(flow, 'InformationFlow.must_conform'))

    @verifies('InformationFlow.must_conform')
    def test_message_channels_preserve_direction_and_require_boundary_mapping(self):
        a, b = Uml.Property(), Uml.Property()
        send = Uml.MessageOccurrenceSpecification(covered=Uml.Lifeline(represents=a))
        receive = Uml.MessageOccurrenceSpecification(covered=Uml.Lifeline(represents=b))
        message = Uml.Message(sendEvent=send, receiveEvent=receive)
        flow = self.flow(realizingMessage=[message])
        flow.informationSource, flow.informationTarget = [a], [b]
        self.assertTrue(check(flow, 'InformationFlow.must_conform'))
        flow.informationTarget = [a]
        self.assertFalse(check(flow, 'InformationFlow.must_conform'))
        flow.informationTarget = [b]
        gate = Uml.Gate()
        message.receiveEvent = gate
        with self.assertRaises(NativeNotImplemented): check(flow, 'InformationFlow.must_conform')
        bind_gate_endpoint(message, gate, b)
        self.assertTrue(check(flow, 'InformationFlow.must_conform'))
        bind_gate_endpoint(message, gate, a)
        self.assertFalse(check(flow, 'InformationFlow.must_conform'))
        message.receiveEvent = None
        with self.assertRaises(NativeNotImplemented): check(flow, 'InformationFlow.must_conform')

    @verifies('InformationFlow.sources_and_targets_kind', 'InformationFlow.convey_classifiers')
    def test_relationship_instances_are_not_flow_participants(self):
        flow = self.flow()
        flow.informationSource = [Uml.OpaqueBehavior(), Uml.InstanceSpecification(classifier=[self.source])]
        self.assertTrue(check(flow, 'InformationFlow.sources_and_targets_kind'))
        flow.informationSource.append(Uml.InstanceSpecification(classifier=[Uml.Association()]))
        self.assertFalse(check(flow, 'InformationFlow.sources_and_targets_kind'))
        flow.conveyed = [Uml.Class(), Uml.Interface(), Uml.Signal(), Uml.Component(), Uml.InformationItem()]
        self.assertTrue(check(flow, 'InformationFlow.convey_classifiers'))
        flow.conveyed.append(Uml.DataType())
        self.assertFalse(check(flow, 'InformationFlow.convey_classifiers'))

    @verifies('InformationItem.has_no', 'InformationItem.not_instantiable')
    def test_abstract_information_items_cannot_have_associations_or_instances(self):
        item = Uml.InformationItem(isAbstract=True)
        self.assertTrue(check(item, 'InformationItem.has_no'))
        self.assertTrue(check(item, 'InformationItem.not_instantiable'))
        association = Uml.Association(ownedEnd=[Uml.Property(type=item), Uml.Property(type=self.target)])
        self.assertFalse(check(item, 'InformationItem.has_no'))
        instance = Uml.InstanceSpecification(classifier=[item])
        self.assertFalse(check(item, 'InformationItem.not_instantiable'))
        instance.classifier.clear()
        self.assertTrue(check(item, 'InformationItem.not_instantiable'))

    @verifies('InformationItem.sources_and_targets')
    def test_represented_item_endpoints_must_be_subsets(self):
        child, abstract = Uml.InformationItem(), Uml.InformationItem()
        abstract.represented.append(child)
        outer = self.flow()
        outer.conveyed = [abstract]
        inner = self.flow()
        inner.conveyed = [child]
        self.assertTrue(check(abstract, 'InformationItem.sources_and_targets'))
        inner.informationSource.append(Uml.Class())
        self.assertFalse(check(abstract, 'InformationItem.sources_and_targets'))
        outer.informationSource.append(inner.informationSource[-1])
        self.assertTrue(check(abstract, 'InformationItem.sources_and_targets'))
        abstract.represented.append(Uml.DataType())
        self.assertFalse(check(abstract, 'InformationItem.sources_and_targets'))
