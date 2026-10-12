"""Redefinition scenarios separated from runtime state-machine execution."""
import unittest
import Uml
from umltools import ModelSession, OperationResultError
from semantic_cases import verifies

Machine = Uml.StateMachines.StateMachine


class RedefinitionCases(unittest.TestCase):
    def setUp(self):
        self.scope = ModelSession()
        self.scope.__enter__()
        self.old_region, self.new_region = Uml.Region(), Uml.Region()
        self.old = Machine(region=[self.old_region])
        self.new = Machine(region=[self.new_region], generalization=[Uml.Generalization(general=self.old)])
        self.new_region.extendedRegion = self.old_region
        self.new.extendedStateMachine.append(self.old)

    def pair(self, cls, **kwargs):
        old, new = cls(**kwargs), cls(**kwargs)
        self.old_region.subvertex.append(old)
        self.new_region.subvertex.append(new)
        new.redefinedVertex = old
        return old, new

    @verifies('StateMachine.isRedefinitionContextValid', 'StateMachine.isConsistentWith', 'Region.isRedefinitionContextValid',
              'Region.isConsistentWith', 'Region-isConsistentWith-pre')
    def test_machine_and_region_redefinitions_with_and_without_classifier_contexts(self):
        self.assertTrue(self.new.isRedefinitionContextValid(self.old))
        self.assertFalse(self.old.isRedefinitionContextValid(self.new))
        self.assertTrue(self.old.isConsistentWith(self.new))  # Unconditional source body.
        self.assertTrue(self.new_region.isRedefinitionContextValid(self.old_region))
        self.assertTrue(self.old_region.isConsistentWith(self.new_region))
        with self.assertRaises(ValueError): self.new_region.isConsistentWith(self.old_region)
        base, child = Uml.Class(), Uml.Class()
        child.generalization.append(Uml.Generalization(general=base))
        base.ownedBehavior.append(self.old)
        child.ownedBehavior.append(self.new)
        self.assertTrue(self.new.isRedefinitionContextValid(self.old))
        child.generalization.clear()
        self.assertFalse(self.new.isRedefinitionContextValid(self.old))

    @verifies('State.isConsistentWith', 'State-isConsistentWith-pre', 'Vertex.isConsistentWith', 'Vertex.isConsistentWith.precondition')
    def test_states_submachines_vertex_interpretation_and_redefined_nested_regions(self):
        old, new = self.pair(Uml.State)
        self.assertTrue(old.isConsistentWith(new))
        self.assertTrue(old.uml_operation('Vertex', 'isConsistentWith', new))
        original = Machine()
        old.submachine = original
        self.assertFalse(old.isConsistentWith(new))
        replacement = Machine(extendedStateMachine=[original])
        new.submachine = replacement
        self.assertTrue(old.isConsistentWith(new))
        old.submachine, new.submachine = None, None
        a, b = Uml.Region(), Uml.Region()
        old.region.append(a)
        new.region.append(b)
        new.redefinedVertex = old
        self.assertTrue(b.isRedefinitionContextValid(a))
        new.redefinedVertex = None
        self.assertFalse(b.isRedefinitionContextValid(a))
        with self.assertRaises(ValueError): new.isConsistentWith(old)

    @verifies('Pseudostate.isConsistentWith', 'Pseudostate-isConsistentWith-pre', 'FinalState.isConsistentWith', 'FinalState-isConsistentWith-pre',
              'ConnectionPointReference.isConsistentWith', 'ConnectionPointReference-isConsistentWith-pre')
    def test_vertex_specializations_check_kind_and_preconditions(self):
        old, new = self.pair(Uml.Pseudostate, kind=Uml.PseudostateKind.choice)
        self.assertTrue(old.isConsistentWith(new))
        new.kind = Uml.PseudostateKind.junction
        self.assertFalse(old.isConsistentWith(new))
        with self.assertRaises(ValueError): new.isConsistentWith(old)
        for cls in (Uml.FinalState, Uml.ConnectionPointReference):
            original, replacement = self.pair(cls)
            self.assertTrue(original.isConsistentWith(replacement))
            with self.assertRaises(ValueError): replacement.isConsistentWith(original)

    @verifies('Transition.isConsistentWith', 'Transition-isConsistentWith-pre')
    def test_transition_redefinition_checks_redefined_source_vertex(self):
        old_source, new_source = self.pair(Uml.State)
        original, replacement = Uml.Transition(source=old_source), Uml.Transition(source=new_source)
        self.old_region.transition.append(original)
        self.new_region.transition.append(replacement)
        self.assertTrue(original.isConsistentWith(replacement))
        new_source.redefinedVertex = None
        self.assertFalse(original.isConsistentWith(replacement))
        with self.assertRaises(ValueError): replacement.isConsistentWith(original)
