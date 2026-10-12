"""Additional channel, represented-item and lifecycle boundary scenarios."""
import unittest
import Uml
from umltools import ModelSession
from umltools.native import check, NativeNotImplemented
from umltools.interaction_mapping import bind_gate_endpoint
from semantic_cases import verifies


class InformationFlowAuditCases(unittest.TestCase):
    def setUp(self):
        self.session = ModelSession()
        self.session.__enter__()

    def tearDown(self): self.session.__exit__(None, None, None)

    @verifies('InformationFlow.must_conform')
    def test_every_realizing_channel_must_conform_and_absent_channels_are_vacuous(self):
        a, b = Uml.Class(), Uml.Class()
        first = Uml.Dependency(client=[a], supplier=[b])
        wrong = Uml.Dependency(client=[a], supplier=[Uml.Class()])
        flow = Uml.InformationFlow(informationSource=[a], informationTarget=[b], realization=[first, wrong])
        self.assertFalse(check(flow, 'InformationFlow.must_conform'))
        wrong.supplier = [b]
        self.assertTrue(check(flow, 'InformationFlow.must_conform'))
        with self.assertRaises(TypeError): Uml.Relationship()  # Abstract channels cannot be manufactured as concrete UML objects.
        flow.realization.clear()
        self.assertTrue(check(flow, 'InformationFlow.must_conform'))  # No channels: separate multiplicity obligations still apply.
        flow.informationTarget.clear()
        self.assertFalse(check(flow, 'InformationFlow.must_conform'))

    @verifies('InformationFlow.sources_and_targets_kind', 'InformationFlow.convey_classifiers')
    def test_allowed_endpoint_families_and_independent_conveyed_classifier_kinds(self):
        allowed = [Uml.Actor(), Uml.Node(), Uml.UseCase(), Uml.Artifact(), Uml.Class(), Uml.Component(), Uml.Port(),
                   Uml.Property(), Uml.Interface(), Uml.Package(), Uml.InitialNode(), Uml.ActivityPartition(),
                   Uml.OpaqueBehavior(), Uml.InstanceSpecification(classifier=[Uml.Class()])]
        flow = Uml.InformationFlow(informationSource=allowed, informationTarget=list(allowed),
                                   conveyed=[Uml.Class(), Uml.Interface(), Uml.InformationItem(), Uml.Signal(), Uml.Component()])
        self.assertTrue(check(flow, 'InformationFlow.sources_and_targets_kind'))
        self.assertTrue(check(flow, 'InformationFlow.convey_classifiers'))
        flow.informationTarget.append(Uml.LiteralInteger())
        self.assertFalse(check(flow, 'InformationFlow.sources_and_targets_kind'))
        flow.informationTarget.pop()
        flow.conveyed.append(Uml.PrimitiveType())
        self.assertFalse(check(flow, 'InformationFlow.convey_classifiers'))

    @verifies('InformationItem.sources_and_targets', 'InformationItem.has_no', 'InformationItem.not_instantiable')
    def test_representation_target_subsets_and_deletion_of_associations_instances(self):
        a, b, foreign = Uml.Class(), Uml.Class(), Uml.Class()
        abstract, represented = Uml.InformationItem(isAbstract=True), Uml.InformationItem(isAbstract=True)
        abstract.represented = [represented]
        outer = Uml.InformationFlow(informationSource=[a], informationTarget=[b], conveyed=[abstract])
        inner = Uml.InformationFlow(informationSource=[a], informationTarget=[b, foreign], conveyed=[represented])
        self.assertFalse(check(abstract, 'InformationItem.sources_and_targets'))
        outer.informationTarget.append(foreign)
        self.assertTrue(check(abstract, 'InformationItem.sources_and_targets'))
        outer.delete()
        self.assertFalse(check(abstract, 'InformationItem.sources_and_targets'))
        inner.delete()
        self.assertTrue(check(abstract, 'InformationItem.sources_and_targets'))
        assoc = Uml.Association(ownedEnd=[Uml.Property(type=abstract), Uml.Property(type=b)])
        instance = Uml.InstanceSpecification(classifier=[abstract])
        self.assertFalse(check(abstract, 'InformationItem.has_no'))
        self.assertFalse(check(abstract, 'InformationItem.not_instantiable'))
        assoc.delete()
        instance.delete()
        self.assertTrue(check(abstract, 'InformationItem.has_no'))
        self.assertTrue(check(abstract, 'InformationItem.not_instantiable'))
        abstract.generalization.append(Uml.Generalization(general=represented))
        self.assertFalse(check(abstract, 'InformationItem.has_no'))

    @verifies('InformationFlow.must_conform')
    def test_gate_mapping_cleanup_and_message_endpoint_replacement(self):
        a, b = Uml.Property(), Uml.Property()
        send = Uml.MessageOccurrenceSpecification(covered=Uml.Lifeline(represents=a))
        gate = Uml.Gate()
        message = Uml.Message(sendEvent=send, receiveEvent=gate)
        flow = Uml.InformationFlow(informationSource=[a], informationTarget=[b], realizingMessage=[message])
        bind_gate_endpoint(message, gate, b)
        self.assertTrue(check(flow, 'InformationFlow.must_conform'))
        b.delete()
        replacement = Uml.Property()
        flow.informationTarget = [replacement]
        with self.assertRaises(NativeNotImplemented): check(flow, 'InformationFlow.must_conform')
        bind_gate_endpoint(message, gate, replacement)
        self.assertTrue(check(flow, 'InformationFlow.must_conform'))
        gate.delete()
        with self.assertRaises(NativeNotImplemented): check(flow, 'InformationFlow.must_conform')
