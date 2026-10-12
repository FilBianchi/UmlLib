import unittest
import Uml
from umltools import ModelSession
from umltools.native import check, NativeNotImplemented
from umltools.interaction_mapping import mark_extra_global, map_occurrence_gate
from semantic_cases import verifies


class DecompositionCases(unittest.TestCase):
    def setUp(self):
        self.scope = ModelSession()
        self.scope.__enter__()
        self.role = Uml.Property(aggregation=Uml.AggregationKind.composite)
        self.owner = Uml.Class(ownedAttribute=[self.role])
        self.outer_line = Uml.Lifeline(represents=self.role)
        self.inner_line = Uml.Lifeline(represents=Uml.Property())
        self.outer = Uml.Interaction(lifeline=[self.outer_line])
        self.inner = Uml.Interaction(lifeline=[self.inner_line])
        self.decomposition = Uml.PartDecomposition(refersTo=self.inner)
        self.outer_line.decomposedAs = self.decomposition

    def tearDown(self): self.scope.__exit__(None, None, None)

    def use_pair(self, outer=None, inner=None):
        referred_line = Uml.Lifeline(represents=self.role)
        counterpart_interaction = Uml.Interaction()
        nested_decomposition = Uml.PartDecomposition(refersTo=counterpart_interaction)
        referred_line.decomposedAs = nested_decomposition
        referred = Uml.Interaction(lifeline=[referred_line])
        a = Uml.InteractionUse(covered=[self.outer_line], refersTo=referred)
        b = Uml.InteractionUse(covered=[self.inner_line], refersTo=counterpart_interaction)
        (outer or self.outer).fragment.append(a)
        (inner or self.inner).fragment.append(b)
        return a, b, referred_line

    def fragment_pair(self, *, operator=Uml.InteractionOperatorKind.opt, outer=None, inner=None):
        a = Uml.CombinedFragment(interactionOperator=operator, covered=[self.outer_line], operand=[Uml.InteractionOperand()])
        b = Uml.CombinedFragment(interactionOperator=operator, covered=[self.inner_line], operand=[Uml.InteractionOperand()])
        (outer or self.outer).fragment.append(a)
        (inner or self.inner).fragment.append(b)
        mark_extra_global(self.decomposition, b)
        return a, b

    def message_pair(self, name='signal', outer=None, inner=None):
        a = Uml.MessageOccurrenceSpecification(covered=self.outer_line)
        internal = Uml.MessageOccurrenceSpecification(covered=self.inner_line)
        gate = Uml.Gate()
        external = Uml.MessageOccurrenceSpecification(covered=Uml.Lifeline())
        outer_message = Uml.Message(name=name, sendEvent=a, receiveEvent=external)
        inner_message = Uml.Message(name=name, sendEvent=internal, receiveEvent=gate)
        self.outer.message.append(outer_message)
        self.inner.message.append(inner_message)
        self.inner.formalGate.append(gate)
        (outer or self.outer).fragment.append(a)
        (inner or self.inner).fragment.append(internal)
        return a, internal, gate

    @verifies('PartDecomposition.parts_of_internal_structures')
    def test_only_internal_composite_parts_can_be_decomposed(self):
        self.assertTrue(check(self.decomposition, 'PartDecomposition.parts_of_internal_structures'))
        self.role.aggregation = Uml.AggregationKind.none
        self.assertFalse(check(self.decomposition, 'PartDecomposition.parts_of_internal_structures'))
        self.owner.ownedAttribute.remove(self.role)
        collaboration = Uml.Collaboration(ownedAttribute=[self.role])
        self.role.aggregation = Uml.AggregationKind.composite
        self.assertFalse(check(self.decomposition, 'PartDecomposition.parts_of_internal_structures'))

    @verifies('PartDecomposition.assume', 'PartDecomposition.commutativity_of_decomposition')
    def test_use_mapping_and_commutativity(self):
        original, counterpart, line = self.use_pair()
        self.assertTrue(check(self.decomposition, 'PartDecomposition.assume'))
        self.assertTrue(check(self.decomposition, 'PartDecomposition.commutativity_of_decomposition'))
        line.decomposedAs.refersTo = Uml.Interaction()
        self.assertFalse(check(self.decomposition, 'PartDecomposition.commutativity_of_decomposition'))

    @verifies('PartDecomposition.assume', 'PartDecomposition.commutativity_of_decomposition')
    def test_nested_operand_use_is_checked(self):
        a, b = self.fragment_pair()
        use, counterpart, line = self.use_pair(a.operand[0], b.operand[0])
        self.assertTrue(check(self.decomposition, 'PartDecomposition.assume'))
        self.assertTrue(check(self.decomposition, 'PartDecomposition.commutativity_of_decomposition'))
        line.decomposedAs = None
        self.assertFalse(check(self.decomposition, 'PartDecomposition.commutativity_of_decomposition'))
        b.operand[0].fragment.clear()
        self.assertFalse(check(self.decomposition, 'PartDecomposition.assume'))

    @verifies('PartDecomposition.assume')
    def test_operand_operator_and_global_coverage_must_correspond(self):
        a, b = self.fragment_pair()
        self.assertTrue(check(self.decomposition, 'PartDecomposition.assume'))
        b.interactionOperator = Uml.InteractionOperatorKind.loop
        self.assertFalse(check(self.decomposition, 'PartDecomposition.assume'))
        b.interactionOperator = a.interactionOperator
        b.operand.append(Uml.InteractionOperand())
        self.assertFalse(check(self.decomposition, 'PartDecomposition.assume'))

    @verifies('PartDecomposition.assume')
    def test_extra_global_status_is_not_inferred_from_coverage_alone(self):
        a, b = self.fragment_pair()
        self.decomposition._extra_global_fragments.clear()
        with self.assertRaises(NativeNotImplemented): check(self.decomposition, 'PartDecomposition.assume')
        mark_extra_global(self.decomposition, b, is_extra_global=False)
        self.assertFalse(check(self.decomposition, 'PartDecomposition.assume'))
        mark_extra_global(self.decomposition, b)
        self.assertTrue(check(self.decomposition, 'PartDecomposition.assume'))

    @verifies('PartDecomposition.assume')
    def test_order_between_gates_and_global_constructs_is_preserved(self):
        event, anchor, gate = self.message_pair()
        a, b, line = self.use_pair()
        self.assertTrue(check(self.decomposition, 'PartDecomposition.assume'))
        self.inner.fragment.reverse()
        self.assertFalse(check(self.decomposition, 'PartDecomposition.assume'))

    @verifies('PartDecomposition.assume')
    def test_order_between_two_occurrences_is_preserved(self):
        self.message_pair('first')
        self.message_pair('second')
        self.assertTrue(check(self.decomposition, 'PartDecomposition.assume'))
        self.inner.fragment.reverse()
        self.assertFalse(check(self.decomposition, 'PartDecomposition.assume'))

    @verifies('PartDecomposition.assume')
    def test_a_formal_gate_cannot_match_two_distinct_occurrences(self):
        self.message_pair()
        other = Uml.MessageOccurrenceSpecification(covered=self.outer_line)
        self.outer.fragment.append(other)
        self.outer.message.append(Uml.Message(name='signal', sendEvent=other))
        self.assertFalse(check(self.decomposition, 'PartDecomposition.assume'))

    @verifies('PartDecomposition.assume')
    def test_operand_gate_cannot_be_moved_into_another_operand(self):
        a, b = self.fragment_pair(operator=Uml.InteractionOperatorKind.alt)
        a.operand.append(Uml.InteractionOperand())
        b.operand.append(Uml.InteractionOperand())
        occurrence, anchor, gate = self.message_pair(outer=a.operand[0], inner=b.operand[0])
        self.assertTrue(check(self.decomposition, 'PartDecomposition.assume'))
        b.operand[0].fragment.remove(anchor)
        b.operand[1].fragment.append(anchor)
        self.assertFalse(check(self.decomposition, 'PartDecomposition.assume'))

    @verifies('PartDecomposition.assume')
    def test_non_message_occurrence_has_an_explicit_gate_mapping(self):
        occurrence = Uml.ExecutionOccurrenceSpecification(covered=self.outer_line)
        self.outer.fragment.append(occurrence)
        internal = Uml.ExecutionOccurrenceSpecification(covered=self.inner_line)
        self.inner.fragment.append(internal)
        actual, formal = Uml.Gate(name='boundary'), Uml.Gate(name='boundary')
        self.decomposition.actualGate.append(actual)
        self.inner.formalGate.append(formal)
        self.outer.message.append(Uml.Message(name='event', sendEvent=actual))
        self.inner.message.append(Uml.Message(name='event', receiveEvent=formal))
        with self.assertRaises(NativeNotImplemented): check(self.decomposition, 'PartDecomposition.assume')
        map_occurrence_gate(self.decomposition, occurrence, actual, internal_occurrence=internal)
        self.assertTrue(check(self.decomposition, 'PartDecomposition.assume'))
        self.decomposition.actualGate.remove(actual)
        self.assertFalse(check(self.decomposition, 'PartDecomposition.assume'))

    @verifies('PartDecomposition.assume')
    def test_internal_partial_uses_do_not_create_extra_global_obligations(self):
        second_line = Uml.Lifeline()
        self.inner.lifeline.append(second_line)
        private_use = Uml.InteractionUse(covered=[self.inner_line], refersTo=Uml.Interaction())
        self.inner.fragment.append(private_use)
        self.assertTrue(check(self.decomposition, 'PartDecomposition.assume'))

    @verifies('PartDecomposition.assume')
    def test_global_counterpart_use_must_cover_every_internal_lifeline(self):
        a, b, line = self.use_pair()
        second_line = Uml.Lifeline()
        self.inner.lifeline.append(second_line)
        self.assertFalse(check(self.decomposition, 'PartDecomposition.assume'))
        b.covered.append(second_line)
        self.assertTrue(check(self.decomposition, 'PartDecomposition.assume'))
