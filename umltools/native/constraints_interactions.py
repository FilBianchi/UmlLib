"""Interaction constraints using explicit graph traversal and message signatures."""
from . import invariant, kind, reverse, single, instances, NativeNotImplemented
from .constraints_basic import predicates, required, enum
from .constraints_actions import conforms, primitive
from .interactions import combined_fragment, operand_fragment, surrounding


def interaction_of(fragment):
    seen = set()
    while fragment is not None:
        if fragment in seen: raise ValueError('Cyclic interaction nesting')
        seen.add(fragment)
        if fragment.enclosingInteraction is not None: return fragment.enclosingInteraction
        fragment = operand_fragment(fragment) if kind(fragment, fragment, 'InteractionOperand') else operand_fragment(fragment.enclosingOperand)
    return None


def fragments(interaction):
    result, pending = [], list(reversed(interaction.fragment))
    while pending:
        fragment = pending.pop()
        if fragment in result: continue
        result.append(fragment)
        if kind(interaction, fragment, 'CombinedFragment'):
            pending.extend(reversed([f for op in fragment.operand for f in op.fragment]))
    return result


def lifeline_equal(a, b):
    if a.represents is not b.represents: return False
    if a.selector is None or b.selector is None: return a.selector is b.selector
    if a.selector is b.selector: return True
    left,right=a.selector,b.selector
    literals={'LiteralBoolean','LiteralInteger','LiteralReal','LiteralString','LiteralUnlimitedNatural','LiteralNull'}
    if left.__spec__.name not in literals or right.__spec__.name not in literals:
        raise NativeNotImplemented('Continuation selector equivalence requires an expression evaluator')
    if left.__spec__.name != right.__spec__.name: return False
    if left.__spec__.name == 'LiteralNull': return True
    if left.value is None or right.value is None:
        raise NativeNotImplemented('Continuation selector value is unspecified')
    return left.value == right.value


def operand_of_constraint(self): return single(reverse(self, 'InteractionOperand', 'guard'))
def gate_parent(self, class_, field): return required(single(reverse(self, class_, field)))


def integer_expression(value):
    value = required(value)
    number = value.integerValue()
    if number is not None: return number
    if value.isComputable(): raise ValueError('Interaction bound must denote Integer')
    raise NativeNotImplemented('Interaction bound requires a numeric expression evaluator')


predicates({
    'CombinedFragment.break': lambda s: enum(s.interactionOperator) != 'break' or set(l for f in surrounding(s) for l in f.covered) == set(s.covered),
    'CombinedFragment.consider_and_ignore': lambda s: enum(s.interactionOperator) not in ('consider', 'ignore') or kind(s, s, 'ConsiderIgnoreFragment'),
    'CombinedFragment.opt_loop_break_neg': lambda s: enum(s.interactionOperator) not in ('opt', 'loop', 'break', 'assert', 'neg') or len(s.operand) == 1,
    'ConsiderIgnoreFragment.consider_or_ignore': lambda s: enum(s.interactionOperator) in ('consider', 'ignore'),
    'ConsiderIgnoreFragment.type': lambda s: all(kind(s, m, 'Operation') or kind(s, m, 'Signal') for m in s.message),
    'Continuation.first_or_last_interaction_fragment': lambda s: s.enclosingOperand is not None and bool(s.enclosingOperand.fragment) and s in (s.enclosingOperand.fragment[0], s.enclosingOperand.fragment[-1]),
    'Continuation.global': lambda s: s.enclosingOperand is not None and bool(s.enclosingOperand.covered) and set(s.enclosingOperand.covered) <= set(s.covered),
    'ExecutionSpecification.same_lifeline': lambda s: required(s.start).covered is required(s.finish).covered,
    'Gate.actual_gate_matched': lambda s: not s.isActual() or sum(g.matches(s) for g in gate_parent(s, 'InteractionUse', 'actualGate').refersTo.formalGate) == 1,
    'Gate.inside_cf_matched': lambda s: not s.isInsideCF() or sum(g.isOutsideCF() and g.matches(s) for g in required(combined_fragment(s)).cfragmentGate) == 1,
    'Gate.formal_gate_distinguishable': lambda s: not s.isFormal() or sum(g.getName() == s.getName() for g in gate_parent(s, 'Interaction', 'formalGate').formalGate) == 1,
    'Gate.actual_gate_distinguishable': lambda s: not s.isActual() or sum(g.getName() == s.getName() for g in gate_parent(s, 'InteractionUse', 'actualGate').actualGate) == 1,
    'Gate.outside_cf_gate_distinguishable': lambda s: not s.isOutsideCF() or sum(g.isOutsideCF() and g.getName() == s.getName() for g in required(combined_fragment(s)).cfragmentGate) == 1,
    'Gate.inside_cf_gate_distinguishable': lambda s: not s.isInsideCF() or sum(g.isInsideCF() and g.getName() == s.getName() and g.getOperand() is s.getOperand() for g in required(combined_fragment(s)).cfragmentGate) == 1,
    'Interaction.not_contained': lambda s: s.enclosingInteraction is None,
    'InteractionConstraint.minint_maxint': lambda s: s.maxint is None and s.minint is None or enum(required(operand_fragment(operand_of_constraint(s))).interactionOperator) == 'loop',
    'InteractionConstraint.minint_non_negative': lambda s: s.minint is None or integer_expression(s.minint) >= 0,
    'InteractionConstraint.maxint_positive': lambda s: s.maxint is None or integer_expression(s.maxint) > 0,
    'InteractionConstraint.maxint_greater_equal_minint': lambda s: s.maxint is None or s.minint is not None and integer_expression(s.maxint) >= integer_expression(s.minint),
    'InteractionUse.gates_match': lambda s: not s.actualGate or all(sum(g.matches(f) for g in s.actualGate) == 1 for f in required(s.refersTo).formalGate) and all(sum(f.matches(g) for f in s.refersTo.formalGate) == 1 for g in s.actualGate),
    'InteractionUse.returnValueRecipient_coverage': lambda s: s.returnValueRecipient is None or any(s.returnValueRecipient in c.allAttributes() for l in s.covered if l.represents is not None for c in s._items(l.represents.type) if kind(s, c, 'Classifier')),
    'InteractionUse.returnValue_type_recipient_correspondence': lambda s: s.returnValue is None or s.returnValue.type is None or s.returnValue.type is required(s.returnValueRecipient).type,
    'Lifeline.selector_specified': lambda s: (s.selector is not None) == (kind(s, s.represents, 'MultiplicityElement') and s.represents.isMultivalued()),
    'Lifeline.selector_int_or_string': lambda s: s.selector is None or kind(s, s.selector, 'LiteralInteger') or kind(s, s.selector, 'LiteralString'),
    'Message.cannot_cross_boundaries': lambda s: s.sendEvent is None or s.receiveEvent is None or set(s.sendEvent.enclosingFragment()) == set(s.receiveEvent.enclosingFragment()),
    'Message.signature_refer_to': lambda s: s.signature is None or s.name == s.signature.name and (kind(s, s.signature, 'Operation') and enum(s.messageSort) in ('asynchCall', 'synchCall', 'reply') or kind(s, s.signature, 'Signal') and enum(s.messageSort) == 'asynchSignal'),
    'PartDecomposition.parts_of_internal_structures': lambda s: all(kind(s, l.represents, 'Property') and kind(s, l.represents.owner, 'StructuredClassifier') and not kind(s, l.represents.owner, 'Collaboration') and l.represents in l.represents.owner.part for l in reverse(s, 'Lifeline', 'decomposedAs')),
})


@invariant('ActionExecutionSpecification.action_referenced')
def execution_action(self):
    parent = interaction_of(self)
    return parent is not None and reverse(required(self.action), 'Interaction', 'action') == [parent]


@invariant('Continuation.same_name')
def continuations(self):
    parent = interaction_of(self)
    if parent is None or self.enclosingOperand is None: return False
    peers = [parent] + ([] if parent.context is None else [b for b in parent.context.ownedBehavior if kind(self, b, 'Interaction')])
    candidates = [f for p in peers for f in fragments(p) if kind(self, f, 'Continuation') and f.name == self.name]
    return all(all(sum(lifeline_equal(a, b) for b in c.covered) == 1 for a in self.covered) and all(sum(lifeline_equal(a, b) for b in self.covered) == 1 for a in c.covered) for c in candidates)


def events(lifeline, operand=None):
    interaction = required(lifeline.interaction)
    return [f for f in fragments(interaction) if kind(lifeline, f, 'OccurrenceSpecification') and lifeline in f._items(f.covered) and (operand is None or f.enclosingOperand is operand)]


@invariant('DestructionOccurrenceSpecification.no_occurrence_specifications_below')
def destruction_last(self):
    if self.enclosingOperand is None: return False
    peers = events(required(self.covered), self.enclosingOperand)
    return bool(peers) and peers[-1] is self


@invariant('Message.sending_receiving_message_event')
def message_order(self):
    if not kind(self, self.receiveEvent, 'MessageOccurrenceSpecification') or not kind(self, self.sendEvent, 'MessageOccurrenceSpecification'): return True
    if self.sendEvent.covered is not self.receiveEvent.covered: return True
    order = events(required(self.sendEvent.covered))
    return order.index(self.sendEvent) < order.index(self.receiveEvent)


@invariant('Gate.outside_cf_matched')
def outside_gates(self):
    if not self.isOutsideCF(): return True
    fragment = required(combined_fragment(self))
    candidates = [g for g in fragment.cfragmentGate if g.isInsideCF() and g.matches(self)]
    if enum(fragment.interactionOperator) == 'alt':
        return all(sum(g.getOperand() is op for g in candidates) == 1 for op in fragment.operand)
    return len(candidates) == 1


@invariant('GeneralOrdering.irreflexive_transitive_closure')
def ordering_acyclic(self):
    pending, seen = [required(self.after)], set()
    while pending:
        occurrence = pending.pop()
        if occurrence is self.before: return False
        if occurrence in seen: continue
        seen.add(occurrence)
        pending.extend(required(g.after) for g in occurrence.toAfter)
    return True


@invariant('Lifeline.same_classifier')
def lifeline_context(self):
    namespace, seen = required(self.represents).namespace, set()
    context = required(self.interaction).context
    while namespace is not None:
        if namespace is context: return True
        if namespace in seen: raise ValueError('Cyclic namespace')
        seen.add(namespace)
        namespace = namespace.namespace
    return False


@invariant('InteractionUse.all_lifelines')
def use_lifelines(self):
    parent = interaction_of(self)
    if parent is None: return False
    return all(l in self.covered for l in parent.lifeline if any(lifeline_equal(l, r) for r in required(self.refersTo).lifeline))


@invariant('Lifeline.interaction_uses_share_lifeline')
def shared_lifelines(self):
    for use in instances(self, 'InteractionUse'):
        if use.refersTo is not self.interaction: continue
        parent = interaction_of(use)
        if parent is None: return False
        for peer in fragments(parent):
            if peer is use or not kind(self, peer, 'InteractionUse'): continue
            if any(lifeline_equal(self, l) for l in required(peer.refersTo).lifeline) and not any(lifeline_equal(self, l) for l in parent.lifeline): return False
    return True


def wildcard(value):
    return kind(value, value, 'Expression') and not value.symbol and not value.operand


@invariant('Message.signature_is_signal')
def signal_signature(self):
    if enum(self.messageSort) != 'asynchSignal' or not kind(self, self.signature, 'Signal'): return True
    attributes = self.signature.allAttributes()
    return len(attributes) == len(self.argument) and all(wildcard(v) or conforms(v.type, p.type) for v, p in zip(self.argument, attributes))


@invariant('Message.signature_is_operation_request')
def request_signature(self):
    if enum(self.messageSort) not in ('asynchCall', 'synchCall') or not kind(self, self.signature, 'Operation'): return True
    parameters = self.signature.inputParameters()
    return len(parameters) == len(self.argument) and all(wildcard(v) or conforms(v.type, p.type) for v, p in zip(self.argument, parameters))


@invariant('Message.signature_is_operation_reply')
def reply_signature(self):
    if enum(self.messageSort) != 'reply' or not kind(self, self.signature, 'Operation'): return True
    parameters = self.signature.outputParameters()
    return len(parameters) == len(self.argument) and all(not kind(self, v, 'Expression') or not v.operand or conforms(v.operand[0].type, p.type) for v, p in zip(self.argument, parameters))


@invariant('Message.occurrence_specifications')
def message_connector(self):
    if not all(kind(self, e, 'MessageOccurrenceSpecification') for e in (self.sendEvent, self.receiveEvent)): return True
    connector = required(self.connector)
    roles = [required(self.sendEvent.covered).represents, required(self.receiveEvent.covered).represents]
    return all(any(e.role is role or e.partWithPort is role for e in connector.end) for role in roles)


@invariant('InteractionUse.arguments_correspond_to_parameters')
def use_parameters(self):
    parameters = required(self.refersTo).inputParameters()
    return len(parameters) == len(self.argument) and all(conforms(a.type, p.type) for a, p in zip(self.argument, parameters))


@invariant('InteractionUse.arguments_are_constants')
def use_arguments(self):
    from ..expression_semantics import expression_fact
    parent = required(interaction_of(self))
    allowed = set(parent.ownedParameter) | (set(parent.context.allAttributes()) if parent.context is not None else set())
    return all(expression_fact(a, 'constant') or set(expression_fact(a, 'references')) <= allowed for a in self.argument)


@invariant('Message.arguments')
def message_arguments(self):
    from ..expression_semantics import expression_fact
    parent = required(single(reverse(self, 'Interaction', 'message')))
    allowed = set(parent.ownedParameter) | (set(parent.context.allAttributes()) if parent.context is not None else set())
    if kind(self, self.sendEvent, 'MessageOccurrenceSpecification'):
        lifeline = required(self.sendEvent.covered)
        if lifeline.represents is not None and kind(self, lifeline.represents.type, 'Classifier'): allowed.update(lifeline.represents.type.allAttributes())
    return all(wildcard(a) or expression_fact(a, 'constant') or set(expression_fact(a, 'references')) <= allowed for a in self.argument)


@invariant('InteractionConstraint.dynamic_variables', 'InteractionConstraint.global_data')
def guard_references(self):
    from ..expression_semantics import expression_fact
    operand = required(operand_of_constraint(self))
    parent = required(interaction_of(operand))
    allowed = set(parent.ownedParameter) | (set(parent.context.allAttributes()) if parent.context is not None else set())
    for l in operand.covered:
        represented = l.represents
        if represented is not None:
            allowed.add(represented)
            if kind(self, represented.type, 'Classifier'): allowed.update(represented.type.allAttributes())
    return all(r in allowed or kind(self, r, 'Property') and r.isReadOnly for r in expression_fact(self.specification, 'references'))


@invariant('InteractionOperand.guard_contain_references')
def operand_references(self):
    return self.guard is None or guard_references(self.guard)


@invariant('InteractionOperand.guard_directly_prior')
def operand_guard_position(self):
    # The metamodel stores the guard on the operand, preceding its ordered fragments.
    # Graphical coordinates belong to UMLDI and are not represented by this model.
    return self.guard is None or self.guard.owner is self
