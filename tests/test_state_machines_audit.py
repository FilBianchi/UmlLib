"""Static state-machine conformance examples; no execution engine is assumed."""
import unittest
import Uml
from umltools import ModelSession
from umltools.native import check
from semantic_cases import verifies

Machine = Uml.StateMachines.StateMachine


class MachineCases(unittest.TestCase):
    def setUp(self):
        self.scope = ModelSession()
        self.scope.__enter__()

    def tearDown(self): self.scope.__exit__(None, None, None)

    def machine(self, *vertices):
        region = Uml.Region(subvertex=list(vertices))
        return Machine(region=[region]), region

    @verifies('State.containingStateMachine', 'Region.containingStateMachine', 'Vertex.containingStateMachine',
              'Vertex.isContainedInState', 'Vertex.isContainedInRegion', 'State.isComposite', 'State.isOrthogonal',
              'State.isSimple', 'State.isSubmachineState', 'StateMachine.LCA', 'StateMachine.LCAState', 'StateMachine.ancestor')
    def test_hierarchical_containment_lcas_and_exact_state_endpoint_types(self):
        outer, sibling, final = Uml.State(), Uml.State(), Uml.FinalState()
        machine, top = self.machine(outer, sibling, final)
        a, b = Uml.State(), Uml.State()
        left, right = Uml.Region(subvertex=[a]), Uml.Region(subvertex=[b])
        outer.region.extend([left, right])
        self.assertIs(a.containingStateMachine(), machine)
        self.assertIs(left.containingStateMachine(), machine)
        self.assertTrue(a.isContainedInState(outer))
        self.assertTrue(a.isContainedInRegion(top))
        self.assertFalse(a.isContainedInRegion(right))
        self.assertTrue(outer.isComposite)
        self.assertTrue(outer.isOrthogonal)
        self.assertTrue(a.isSimple)
        self.assertFalse(a.isSubmachineState)
        self.assertTrue(machine.ancestor(a, outer))
        self.assertFalse(machine.ancestor(outer, a))
        self.assertTrue(machine.ancestor(a, a))
        self.assertIs(machine.LCA(a, b), top)
        self.assertIs(machine.LCAState(a, b), outer)
        self.assertIs(machine.LCAState(a, a), a)
        self.assertIsNone(machine.LCAState(final, final))  # OCL isTypeOf(State) excludes FinalState.
        entry = Uml.Pseudostate(kind=Uml.PseudostateKind.entryPoint)
        outer.connectionPoint.append(entry)
        self.assertIs(entry.containingStateMachine(), machine)
        transition = Uml.Transition(source=entry, target=sibling)
        top.transition.append(transition)
        self.assertTrue(check(transition, 'Transition.transition_vertices'))

    @verifies('Vertex.incoming', 'Vertex.outgoing', 'Transition.containingStateMachine', 'Transition.transition_vertices',
              'Vertex.redefinitionContext', 'Transition.redefinitionContext', 'Region.redefinitionContext')
    def test_transition_navigation_updates_and_rejects_other_machines(self):
        a, b = Uml.State(), Uml.State()
        machine, region = self.machine(a, b)
        transition = Uml.Transition(source=a, target=b)
        region.transition.append(transition)
        self.assertEqual(list(a.outgoing), [transition])
        self.assertEqual(list(b.incoming), [transition])
        self.assertIs(transition.containingStateMachine(), machine)
        for obj, owner in ((a, 'Vertex'), (transition, 'Transition'), (region, 'Region')):
            self.assertIs(obj.uml_operation(owner, 'redefinitionContext'), machine)
        self.assertTrue(check(transition, 'Transition.transition_vertices'))
        foreign = Uml.State()
        other, _ = self.machine(foreign)
        transition.target = foreign
        self.assertFalse(check(transition, 'Transition.transition_vertices'))
        self.assertEqual(list(b.incoming), [])
        transition.delete()
        self.assertEqual(list(a.outgoing), [])

    @verifies('Region.deep_history_vertex', 'Region.shallow_history_vertex', 'Region.initial_vertex', 'Region.owned')
    def test_region_singletons_and_composite_owner_exclusivity(self):
        machine, region = self.machine()
        self.assertTrue(check(region, 'Region.owned'))
        with self.assertRaises(ValueError): Uml.State(region=[region])
        self.assertIs(region.owner, machine)
        for kind, rule in ((Uml.PseudostateKind.deepHistory, 'deep_history_vertex'),
                           (Uml.PseudostateKind.shallowHistory, 'shallow_history_vertex'), (Uml.PseudostateKind.initial, 'initial_vertex')):
            first, second = Uml.Pseudostate(kind=kind), Uml.Pseudostate(kind=kind)
            region.subvertex.append(first)
            self.assertTrue(check(region, 'Region.' + rule))
            region.subvertex.append(second)
            self.assertFalse(check(region, 'Region.' + rule))
            second.delete()
            self.assertTrue(check(region, 'Region.' + rule))

    @verifies('State.entry_or_exit', 'State.composite_states', 'State.submachine_states', 'State.destinations_or_sources_of_transitions',
              'State.submachine_or_regions', 'ConnectionPointReference.entry_pseudostates', 'ConnectionPointReference.exit_pseudostates')
    def test_state_connection_points_submachine_references_and_exclusive_regions(self):
        state = Uml.State()
        machine, top = self.machine(state)
        point = Uml.Pseudostate(kind=Uml.PseudostateKind.entryPoint)
        state.connectionPoint.append(point)
        self.assertTrue(check(state, 'State.entry_or_exit'))
        self.assertFalse(check(state, 'State.composite_states'))
        state.region.append(Uml.Region())
        self.assertTrue(check(state, 'State.composite_states'))
        point.kind = Uml.PseudostateKind.choice
        self.assertFalse(check(state, 'State.entry_or_exit'))
        child = Machine(connectionPoint=[Uml.Pseudostate(kind=Uml.PseudostateKind.entryPoint), Uml.Pseudostate(kind=Uml.PseudostateKind.exitPoint)])
        state.submachine = child
        self.assertFalse(check(state, 'State.submachine_or_regions'))
        self.assertFalse(check(state, 'State.submachine_states'))
        reference = Uml.ConnectionPointReference(entry=[child.connectionPoint[0]], exit=[child.connectionPoint[1]])
        state.connection.append(reference)
        self.assertTrue(check(state, 'State.submachine_states'))
        self.assertTrue(check(reference, 'ConnectionPointReference.entry_pseudostates'))
        self.assertTrue(check(reference, 'ConnectionPointReference.exit_pseudostates'))
        self.assertTrue(check(state, 'State.destinations_or_sources_of_transitions'))
        self.assertIs(reference.containingStateMachine(), machine)
        reference.exit = [child.connectionPoint[0]]
        self.assertFalse(check(reference, 'ConnectionPointReference.exit_pseudostates'))
        foreign = Machine(connectionPoint=[Uml.Pseudostate(kind=Uml.PseudostateKind.entryPoint)])
        reference.entry = [foreign.connectionPoint[0]]
        self.assertFalse(check(state, 'State.destinations_or_sources_of_transitions'))

    @verifies('Pseudostate.choice_vertex', 'Pseudostate.junction_vertex', 'Pseudostate.initial_vertex', 'Pseudostate.history_vertices', 'Pseudostate.outgoing_from_initial')
    def test_pseudostate_degree_rules_and_initial_guard_trigger_restrictions(self):
        start, target, pseudo = Uml.State(), Uml.State(), Uml.Pseudostate(kind=Uml.PseudostateKind.choice)
        machine, region = self.machine(start, target, pseudo)
        self.assertFalse(check(pseudo, 'Pseudostate.choice_vertex'))
        incoming, outgoing = Uml.Transition(source=start, target=pseudo), Uml.Transition(source=pseudo, target=target)
        region.transition.extend([incoming, outgoing])
        self.assertTrue(check(pseudo, 'Pseudostate.choice_vertex'))
        pseudo.kind = Uml.PseudostateKind.junction
        self.assertTrue(check(pseudo, 'Pseudostate.junction_vertex'))
        pseudo.kind = Uml.PseudostateKind.initial
        self.assertTrue(check(pseudo, 'Pseudostate.initial_vertex'))
        outgoing.guard = Uml.Constraint()
        self.assertFalse(check(pseudo, 'Pseudostate.outgoing_from_initial'))
        outgoing.guard = None
        outgoing.trigger.append(Uml.Trigger(event=Uml.AnyReceiveEvent()))
        self.assertFalse(check(pseudo, 'Pseudostate.outgoing_from_initial'))
        region.transition.append(Uml.Transition(source=pseudo, target=start))
        self.assertFalse(check(pseudo, 'Pseudostate.initial_vertex'))
        pseudo.kind = Uml.PseudostateKind.deepHistory
        self.assertFalse(check(pseudo, 'Pseudostate.history_vertices'))

    @verifies('Pseudostate.fork_vertex', 'Pseudostate.join_vertex', 'Pseudostate.transitions_outgoing', 'Pseudostate.transitions_incoming')
    def test_fork_join_distinct_endpoints_and_orthogonal_regions(self):
        outer, source, target = Uml.State(), Uml.State(), Uml.State()
        machine, top = self.machine(outer, source, target)
        a, b = Uml.State(), Uml.State()
        outer.region.extend([Uml.Region(subvertex=[a]), Uml.Region(subvertex=[b])])
        fork, join = Uml.Pseudostate(kind=Uml.PseudostateKind.fork), Uml.Pseudostate(kind=Uml.PseudostateKind.join)
        top.subvertex.extend([fork, join])
        branches = [Uml.Transition(source=fork, target=a), Uml.Transition(source=fork, target=b)]
        arrivals = [Uml.Transition(source=a, target=join), Uml.Transition(source=b, target=join)]
        top.transition.extend([Uml.Transition(source=source, target=fork), *branches, *arrivals, Uml.Transition(source=join, target=target)])
        for obj, rule in ((fork, 'fork_vertex'), (fork, 'transitions_outgoing'), (join, 'join_vertex'), (join, 'transitions_incoming')):
            self.assertTrue(check(obj, 'Pseudostate.' + rule))
        branches[1].target = a
        arrivals[1].source = a
        self.assertFalse(check(fork, 'Pseudostate.transitions_outgoing'))
        self.assertFalse(check(join, 'Pseudostate.transitions_incoming'))
        branches[1].delete()
        self.assertFalse(check(fork, 'Pseudostate.fork_vertex'))

    @verifies('Transition.state_is_internal', 'Transition.state_is_local', 'Transition.state_is_external', 'Transition.outgoing_pseudostates',
              'Transition.initial_transition', 'Transition.join_segment_guards', 'Transition.fork_segment_guards',
              'Transition.join_segment_state', 'Transition.fork_segment_state')
    def test_transition_kinds_and_pseudostate_segments(self):
        a, b, fork, join, entry = Uml.State(), Uml.State(), Uml.Pseudostate(kind=Uml.PseudostateKind.fork), Uml.Pseudostate(kind=Uml.PseudostateKind.join), Uml.Pseudostate(kind=Uml.PseudostateKind.entryPoint)
        machine, region = self.machine(a, b, fork, join, entry)
        transition = Uml.Transition(source=a, target=b, kind=Uml.TransitionKind.internal)
        region.transition.append(transition)
        self.assertFalse(check(transition, 'Transition.state_is_internal'))
        transition.target = a
        self.assertTrue(check(transition, 'Transition.state_is_internal'))
        transition.kind = Uml.TransitionKind.local
        self.assertFalse(check(transition, 'Transition.state_is_local'))
        a.region.append(Uml.Region())
        self.assertTrue(check(transition, 'Transition.state_is_local'))
        transition.source = entry
        transition.kind = Uml.TransitionKind.external
        self.assertFalse(check(transition, 'Transition.state_is_external'))
        transition.source, transition.target = fork, b
        self.assertTrue(check(transition, 'Transition.fork_segment_state'))
        transition.target = join
        self.assertFalse(check(transition, 'Transition.fork_segment_state'))
        self.assertFalse(check(transition, 'Transition.join_segment_state'))
        transition.source = a
        self.assertTrue(check(transition, 'Transition.join_segment_state'))
        transition.trigger.append(Uml.Trigger(event=Uml.AnyReceiveEvent()))
        self.assertFalse(check(transition, 'Transition.join_segment_guards'))
        transition.source, transition.target = fork, b
        self.assertFalse(check(transition, 'Transition.fork_segment_guards'))
        self.assertFalse(check(transition, 'Transition.outgoing_pseudostates'))
        self.assertFalse(check(transition, 'Transition.initial_transition'))

    @verifies('FinalState.no_entry_behavior', 'FinalState.no_exit_behavior', 'FinalState.no_state_behavior', 'FinalState.no_regions',
              'FinalState.no_outgoing_transitions', 'FinalState.cannot_reference_submachine')
    def test_final_state_has_no_behaviors_regions_submachine_or_outgoing_edges(self):
        final, other = Uml.FinalState(), Uml.State()
        machine, region = self.machine(final, other)
        for name, rule in (('entry', 'no_entry_behavior'), ('exit', 'no_exit_behavior'), ('doActivity', 'no_state_behavior')):
            self.assertTrue(check(final, 'FinalState.' + rule))
            setattr(final, name, Uml.OpaqueBehavior())
            self.assertFalse(check(final, 'FinalState.' + rule))
        final.region.append(Uml.Region())
        self.assertFalse(check(final, 'FinalState.no_regions'))
        final.submachine = Machine()
        self.assertFalse(check(final, 'FinalState.cannot_reference_submachine'))
        region.transition.append(Uml.Transition(source=final, target=other))
        self.assertFalse(check(final, 'FinalState.no_outgoing_transitions'))

    @verifies('StateMachine.connection_points', 'StateMachine.classifier_context', 'StateMachine.method', 'StateMachine.context_classifier')
    def test_machine_method_context_and_connection_point_kinds(self):
        machine, region = self.machine()
        owner, other = Uml.Class(), Uml.Class()
        owner.ownedBehavior.append(machine)
        operation = Uml.Operation()
        owner.ownedOperation.append(operation)
        self.assertTrue(check(machine, 'StateMachine.classifier_context'))
        machine.specification = operation
        self.assertTrue(check(machine, 'StateMachine.context_classifier'))
        point = Uml.Pseudostate(kind=Uml.PseudostateKind.entryPoint)
        machine.connectionPoint.append(point)
        self.assertTrue(check(machine, 'StateMachine.connection_points'))
        self.assertFalse(check(machine, 'StateMachine.method'))
        point.kind = Uml.PseudostateKind.initial
        self.assertFalse(check(machine, 'StateMachine.connection_points'))
        owner.ownedOperation.remove(operation)
        other.ownedOperation.append(operation)
        self.assertFalse(check(machine, 'StateMachine.context_classifier'))

    @verifies('Region.belongsToPSM', 'ProtocolStateMachine.classifier_context', 'ProtocolStateMachine.deep_or_shallow_history',
              'ProtocolStateMachine.entry_exit_do', 'ProtocolStateMachine.protocol_transitions', 'ProtocolTransition.referred',
              'ProtocolTransition.refers_to_operation', 'ProtocolTransition.associated_actions', 'ProtocolTransition.belongs_to_psm')
    def test_protocol_rules_include_nested_owned_regions_and_operation_references(self):
        leaf, outer = Uml.State(), Uml.State()
        nested = Uml.Region(subvertex=[leaf])
        outer.region.append(nested)
        root = Uml.Region(subvertex=[outer])
        protocol = Uml.ProtocolStateMachine(region=[root])
        owner = Uml.Class(ownedBehavior=[protocol])
        self.assertTrue(check(protocol, 'ProtocolStateMachine.classifier_context'))
        self.assertTrue(root.belongsToPSM())
        self.assertTrue(nested.belongsToPSM())
        history = Uml.Pseudostate(kind=Uml.PseudostateKind.deepHistory)
        nested.subvertex.append(history)
        self.assertFalse(check(protocol, 'ProtocolStateMachine.deep_or_shallow_history'))
        leaf.entry = Uml.OpaqueBehavior()
        self.assertFalse(check(protocol, 'ProtocolStateMachine.entry_exit_do'))
        transition = Uml.ProtocolTransition(source=leaf, target=leaf)
        nested.transition.append(transition)
        self.assertTrue(check(protocol, 'ProtocolStateMachine.protocol_transitions'))
        operation = Uml.Operation()
        owner.ownedOperation.append(operation)
        transition.trigger.extend([Uml.Trigger(event=Uml.CallEvent(operation=operation)), Uml.Trigger(event=Uml.CallEvent(operation=operation))])
        self.assertEqual(list(transition.referred), [operation])
        self.assertTrue(check(transition, 'ProtocolTransition.refers_to_operation'))
        self.assertTrue(check(transition, 'ProtocolTransition.belongs_to_psm'))
        self.assertTrue(check(transition, 'ProtocolTransition.associated_actions'))
        transition.effect = Uml.OpaqueBehavior()
        self.assertFalse(check(transition, 'ProtocolTransition.associated_actions'))
        owner.ownedOperation.remove(operation)
        self.assertFalse(check(transition, 'ProtocolTransition.refers_to_operation'))
        nested.transition.append(Uml.Transition(source=leaf, target=leaf))
        self.assertFalse(check(protocol, 'ProtocolStateMachine.protocol_transitions'))
