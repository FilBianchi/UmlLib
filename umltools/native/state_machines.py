"""Native state-machine containment queries and structural invariants."""
from . import query, invariant, kind, instances


def enum(value): return None if value is None else value.value
def pseudostate(self, value, name): return kind(self, value, 'Pseudostate') and enum(value.kind) == name


@query('Vertex.incoming')
def incoming(self): return [transition for transition in instances(self, 'Transition') if transition.target is self]


@query('Vertex.outgoing')
def outgoing(self): return [transition for transition in instances(self, 'Transition') if transition.source is self]


@query('Vertex.containingStateMachine')
def vertex_machine(self):
    if self.container is not None: return self.container.containingStateMachine()
    if kind(self, self, 'Pseudostate') and enum(self.kind) in ('entryPoint', 'exitPoint'): return self.stateMachine
    if kind(self, self, 'ConnectionPointReference'):
        if self.state is None: raise ValueError('Connection point has no state')
        return self.state.containingStateMachine()
    return None


@query('State.containingStateMachine', 'Transition.containingStateMachine')
def contained_machine(self):
    if self.container is None: raise ValueError('State or transition has no containing region')
    return self.container.containingStateMachine()


@query('Region.containingStateMachine')
def region_machine(self):
    if self.stateMachine is not None: return self.stateMachine
    if self.state is None: raise ValueError('Region has no containing state or machine')
    return self.state.containingStateMachine()


@query('Region.belongsToPSM')
def protocol_region(self): return kind(self, self.containingStateMachine(), 'ProtocolStateMachine')


@query('State.isComposite')
def composite(self): return bool(self.region)


@query('State.isOrthogonal')
def orthogonal(self): return len(self.region) > 1


@query('State.isSubmachineState')
def submachine_state(self): return self.submachine is not None


@query('State.isSimple')
def simple(self): return not self.region and self.submachine is None


@query('Vertex.redefinitionContext', 'Transition.redefinitionContext', 'Region.redefinitionContext')
def redefinition_context(self): return self.containingStateMachine()


def enclosing_states(vertex):
    result, seen = [], set()
    current = vertex
    while current is not None:
        if id(current) in seen: raise ValueError('Cyclic state containment')
        seen.add(id(current))
        container = current.container
        if container is None or container.state is None: break
        result.append(container.state)
        current = container.state
    return result


@query('Vertex.isContainedInState')
def contained_in_state(self, s): return s.isComposite and s in enclosing_states(self)


@query('Vertex.isContainedInRegion')
def contained_in_region(self, r):
    current = self
    for vertex in [current] + enclosing_states(current):
        if vertex.container is r: return True
    return False


@query('StateMachine.ancestor')
def ancestor(self, s1, s2):
    # Follow the prose: s2 is an ancestor of s1, including equality.
    return s1 is s2 or s2 in enclosing_states(s1)


@query('StateMachine.LCA')
def lca(self, s1, s2):
    first = [vertex.container for vertex in [s1] + enclosing_states(s1) if vertex.container is not None]
    second = [vertex.container for vertex in [s2] + enclosing_states(s2) if vertex.container is not None]
    return next((region for region in first if region in second), None)


@query('StateMachine.LCAState')
def lca_state(self, v1, v2):
    first = ([v1] if kind(self, v1, 'State') else []) + enclosing_states(v1)
    second = ([v2] if kind(self, v2, 'State') else []) + enclosing_states(v2)
    return next((state for state in first if state in second), None)


@query('StateMachine.isConsistentWith')
def machine_consistency(self, redefiningElement): return True


@query('Region.isConsistentWith')
def region_consistency(self, redefiningElement):
    if not redefiningElement.isRedefinitionContextValid(self): raise ValueError('Invalid redefinition context')
    return True


@query('StateMachine.isRedefinitionContextValid')
def machine_redefinition(self, redefinedElement):
    if not kind(self, redefinedElement, 'StateMachine'): return False
    parent_context = redefinedElement.context
    if self.context is None: return parent_context is None and redefinedElement in self.allParents()
    return parent_context is not None and parent_context in self.context.allParents()


@query('Region.isRedefinitionContextValid')
def region_redefinition(self, redefinedElement):
    if not kind(self, redefinedElement, 'Region'): return False
    if self.stateMachine is None:
        return self.state is not None and self.state.redefinedState is not None and redefinedElement in self.state.redefinedState.region
    return any(redefinedElement in machine.region for machine in self.stateMachine.extendedStateMachine)


@query('State.isConsistentWith')
def state_consistency(self, redefiningElement):
    if not redefiningElement.isRedefinitionContextValid(self): raise ValueError('Invalid redefinition context')
    if type(redefiningElement) is not self.__registry__['State']: return False
    return self.submachine is None or (redefiningElement.submachine is not None and self.submachine in redefiningElement.submachine.extendedStateMachine)


@query('Pseudostate.isConsistentWith')
def pseudostate_consistency(self, redefiningElement):
    if not redefiningElement.isRedefinitionContextValid(self): raise ValueError('Invalid redefinition context')
    return kind(self, redefiningElement, 'Pseudostate') and redefiningElement.kind == self.kind


@query('FinalState.isConsistentWith')
def final_consistency(self, redefiningElement):
    if not redefiningElement.isRedefinitionContextValid(self): raise ValueError('Invalid redefinition context')
    return kind(self, redefiningElement, 'FinalState')


@query('ConnectionPointReference.isConsistentWith')
def connection_consistency(self, redefiningElement):
    if not redefiningElement.isRedefinitionContextValid(self): raise ValueError('Invalid redefinition context')
    return kind(self, redefiningElement, 'ConnectionPointReference')


@invariant('State.entry_or_exit', 'StateMachine.connection_points')
def entry_or_exit(self): return all(enum(point.kind) in ('entryPoint', 'exitPoint') for point in self.connectionPoint)


@invariant('State.submachine_states')
def submachine_connections(self): return not self.isSubmachineState or bool(self.connection)


@invariant('State.composite_states')
def composite_connections(self): return not self.connectionPoint or self.isComposite


@invariant('State.destinations_or_sources_of_transitions')
def submachine_endpoints(self):
    return not self.isSubmachineState or all(point.stateMachine is self.submachine for connection in self.connection for point in list(connection.entry) + list(connection.exit))


@invariant('State.submachine_or_regions')
def submachine_or_regions(self): return not self.isComposite or not self.isSubmachineState


@invariant('Region.deep_history_vertex')
def one_deep_history(self): return sum(pseudostate(self, vertex, 'deepHistory') for vertex in self.subvertex) <= 1


@invariant('Region.shallow_history_vertex')
def one_shallow_history(self): return sum(pseudostate(self, vertex, 'shallowHistory') for vertex in self.subvertex) <= 1


@invariant('Region.initial_vertex')
def one_initial(self): return sum(pseudostate(self, vertex, 'initial') for vertex in self.subvertex) <= 1


@invariant('Region.owned')
def exclusive_region_owner(self): return self.stateMachine is None or self.state is None


@invariant('Pseudostate.choice_vertex')
def choice(self): return enum(self.kind) != 'choice' or bool(self.incoming) and bool(self.outgoing)


@invariant('Pseudostate.junction_vertex')
def junction(self): return enum(self.kind) != 'junction' or bool(self.incoming) and bool(self.outgoing)


@invariant('Pseudostate.join_vertex')
def join(self): return enum(self.kind) != 'join' or len(self.outgoing) == 1 and len(self.incoming) >= 2


@invariant('Pseudostate.fork_vertex')
def fork(self): return enum(self.kind) != 'fork' or len(self.incoming) == 1 and len(self.outgoing) >= 2


@invariant('Pseudostate.history_vertices')
def history(self): return enum(self.kind) not in ('deepHistory', 'shallowHistory') or len(self.outgoing) <= 1


@invariant('Pseudostate.initial_vertex')
def initial(self): return enum(self.kind) != 'initial' or len(self.outgoing) <= 1


@invariant('Pseudostate.outgoing_from_initial')
def initial_outgoing(self): return enum(self.kind) != 'initial' or all(transition.guard is None and not transition.trigger for transition in self.outgoing)


def orthogonal_endpoints(self, vertices):
    machine = self.containingStateMachine()
    if machine is None: raise ValueError('Pseudostate has no containing machine')
    # "Any pair" means distinct transition endpoints, not a transition paired with itself.
    for index, first in enumerate(vertices):
        for second in vertices[index+1:]:
            state = machine.LCAState(first, second)
            if state is None or not any(r1 is not r2 and first.isContainedInRegion(r1) and second.isContainedInRegion(r2) for r1 in state.region for r2 in state.region): return False
    return True


@invariant('Pseudostate.transitions_outgoing')
def orthogonal_fork(self): return enum(self.kind) != 'fork' or orthogonal_endpoints(self, [transition.target for transition in self.outgoing])


@invariant('Pseudostate.transitions_incoming')
def orthogonal_join(self): return enum(self.kind) != 'join' or orthogonal_endpoints(self, [transition.source for transition in self.incoming])


@invariant('FinalState.no_exit_behavior')
def no_exit(self): return self.exit is None


@invariant('FinalState.no_entry_behavior')
def no_entry(self): return self.entry is None


@invariant('FinalState.no_state_behavior')
def no_activity(self): return self.doActivity is None


@invariant('FinalState.no_regions')
def no_regions(self): return not self.region


@invariant('FinalState.no_outgoing_transitions')
def no_outgoing(self): return not self.outgoing


@invariant('FinalState.cannot_reference_submachine')
def no_submachine(self): return self.submachine is None


@invariant('ConnectionPointReference.entry_pseudostates')
def connection_entries(self): return all(enum(point.kind) == 'entryPoint' for point in self.entry)


@invariant('ConnectionPointReference.exit_pseudostates')
def connection_exits(self): return all(enum(point.kind) == 'exitPoint' for point in self.exit)


@invariant('Transition.state_is_external')
def external(self): return enum(self.kind) != 'external' or not pseudostate(self, self.source, 'entryPoint')


@invariant('Transition.state_is_internal')
def internal(self): return enum(self.kind) != 'internal' or kind(self, self.source, 'State') and self.source is self.target


@invariant('Transition.state_is_local')
def local(self): return enum(self.kind) != 'local' or kind(self, self.source, 'State') and self.source.isComposite or pseudostate(self, self.source, 'entryPoint')


@invariant('Transition.join_segment_guards')
def join_guards(self): return not pseudostate(self, self.target, 'join') or self.guard is None and not self.trigger


@invariant('Transition.fork_segment_guards')
def fork_guards(self): return not pseudostate(self, self.source, 'fork') or self.guard is None and not self.trigger


@invariant('Transition.join_segment_state')
def join_source(self): return not pseudostate(self, self.target, 'join') or kind(self, self.source, 'State')


@invariant('Transition.fork_segment_state')
def fork_target(self): return not pseudostate(self, self.source, 'fork') or kind(self, self.target, 'State')


@invariant('Transition.outgoing_pseudostates')
def pseudostate_triggers(self): return not kind(self, self.source, 'Pseudostate') or enum(self.source.kind) == 'initial' or not self.trigger


@invariant('Transition.initial_transition')
def initial_trigger(self):
    if not kind(self, self.source, 'Pseudostate'): return True
    if self.container is None: raise ValueError('Transition has no region')
    return self.container.stateMachine is None or not self.trigger


@invariant('Transition.transition_vertices')
def vertices_in_machine(self):
    if self.source is None or self.target is None: raise ValueError('Transition endpoint missing')
    machine = self.containingStateMachine()
    return self.source.containingStateMachine() is machine and self.target.containingStateMachine() is machine


@invariant('StateMachine.classifier_context')
def classifier_context(self): return self.context is None or not kind(self, self.context, 'Interface')


@invariant('StateMachine.method')
def method_connections(self): return self.specification is None or not self.connectionPoint


@invariant('StateMachine.context_classifier')
def context_classifier(self): return self.specification is None or self.context is not None and self.context in self._items(self.specification.featuringClassifier)
