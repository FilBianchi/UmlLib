"""Ordered, recursive part-decomposition projection (UML 17.12.24)."""
from . import invariant, kind, reverse, NativeNotImplemented
from .constraints_basic import required
from .constraints_interactions import lifeline_equal, fragments


def covers(self, fragment, lifeline):
    if lifeline in fragment._items(fragment.covered): return True
    if kind(self, fragment, 'CombinedFragment'):
        return any(covers(self, child, lifeline) for op in fragment.operand for child in op.fragment)
    return False


def global_construct(self, fragment, all_lifelines):
    if kind(self, fragment, 'InteractionUse'):
        return bool(all_lifelines) and set(fragment.covered) == all_lifelines
    if not kind(self, fragment, 'CombinedFragment'): return False
    extra = getattr(self, '_extra_global_fragments', {}).get(fragment)
    if extra is None:
        if set(fragment.covered) == all_lifelines:
            raise NativeNotImplemented('Extra-global CombinedFragment status requires mark_extra_global')
        return False
    if extra and set(fragment.covered) != all_lifelines:
        raise ValueError('An extra-global fragment must cover every decomposition lifeline')
    return extra


def paths(self, container, prefix=()):
    result = {}
    def visit(container, prefix, active):
        if container in active: raise ValueError('Cyclic interaction containment')
        for index, fragment in enumerate(container.fragment):
            result[fragment] = prefix + (index,)
            if kind(self, fragment, 'CombinedFragment'):
                for op_index, operand in enumerate(fragment.operand):
                    visit(operand, prefix + (index, op_index), active | {container})
    visit(container, prefix, set())
    return result


def occurrence_match(self, occurrence, target_paths):
    explicit = getattr(self, '_occurrence_gate_mappings', {}).get(occurrence)
    if explicit is not None:
        actual_gate, anchor = explicit
        if actual_gate not in self.actualGate: return None
        matches = [g for g in self.refersTo.formalGate if actual_gate.matches(g)]
    elif kind(self, occurrence, 'MessageOccurrenceSpecification'):
        message = required(occurrence.message)
        send = occurrence.isSend()
        name = ('out_' if send else 'in_') + required(message.name)
        matches = [g for g in self.refersTo.formalGate if g.getName() == name
                   and required(g.message).signature is message.signature
                   and g.message.messageSort == message.messageSort
                   and (g.isReceive() if send else g.isSend())]
        anchor = None
    else:
        raise NativeNotImplemented('Execution occurrence requires map_occurrence_gate')
    if len(matches) != 1: return None
    gate = matches[0]
    if anchor is None:
        ends = gate.oppositeEnd()
        if len(ends) == 1 and kind(self, ends[0], 'OccurrenceSpecification'): anchor = ends[0]
        else: raise NativeNotImplemented('Gate order requires an internal occurrence anchor')
    if anchor not in target_paths: return None
    if explicit is not None and kind(self, occurrence, 'MessageOccurrenceSpecification'):
        actual_gate = explicit[0]
        if actual_gate.isSend() != occurrence.isSend() or actual_gate.isReceive() != occurrence.isReceive(): return None
    return gate, target_paths[anchor]


def decomposition_pairs(self, lifeline):
    source = required(lifeline.interaction)
    target = required(self.refersTo)
    all_lifelines = set(target.lifeline)
    if not all_lifelines: return None
    target_paths = paths(self, target)
    pairs, used_gates = [], set()
    invalid = False

    def compare(original, decomposed, prefix=()):
        nonlocal invalid
        original_sequence = [f for f in original.fragment if covers(self, f, lifeline)
                             and any(kind(self, f, n) for n in ('CombinedFragment', 'InteractionUse', 'OccurrenceSpecification'))]
        source_constructs = [f for f in original_sequence if not kind(self, f, 'OccurrenceSpecification')]
        target_constructs = [f for f in decomposed.fragment if global_construct(self, f, all_lifelines)]
        if len(source_constructs) != len(target_constructs):
            invalid = True
            return
        mapping = dict(zip(source_constructs, target_constructs))
        anchors = []
        for a in original_sequence:
            if kind(self, a, 'OccurrenceSpecification'):
                match = occurrence_match(self, a, target_paths)
                if match is None or match[0] in used_gates:
                    invalid = True
                    return
                gate, position = match
                # A gate cannot move an occurrence into another matched operand.
                if position[:len(prefix)] != prefix:
                    invalid = True
                    return
                used_gates.add(gate)
                anchors.append(position)
                continue
            b = mapping[a]
            if kind(self, a, 'CombinedFragment'):
                if not kind(self, b, 'CombinedFragment') or a.interactionOperator != b.interactionOperator or len(a.operand) != len(b.operand):
                    invalid = True
                    return
                for op_a, op_b in zip(a.operand, b.operand):
                    op_index = list(b.operand).index(op_b)
                    compare(op_a, op_b, target_paths[b] + (op_index,))
            elif not kind(self, b, 'InteractionUse'):
                invalid = True
                return
            pairs.append((a, b))
            anchors.append(target_paths[b])
        if any(a >= b for a, b in zip(anchors, anchors[1:])): invalid = True

    compare(source, target)
    return None if invalid else pairs


@invariant('PartDecomposition.assume')
def decomposition_structure(self):
    lifelines = reverse(self, 'Lifeline', 'decomposedAs')
    return bool(lifelines) and all(decomposition_pairs(self, l) is not None for l in lifelines)


@invariant('PartDecomposition.commutativity_of_decomposition')
def decomposition_commutes(self):
    lifelines = reverse(self, 'Lifeline', 'decomposedAs')
    if not lifelines: return False
    for lifeline in lifelines:
        pairs = decomposition_pairs(self, lifeline)
        if pairs is None: return False
        for original, counterpart in pairs:
            if not kind(self, original, 'InteractionUse'): continue
            matching = [l for l in required(original.refersTo).lifeline if lifeline_equal(l, lifeline)]
            if len(matching) != 1 or matching[0].decomposedAs is None or matching[0].decomposedAs.refersTo is not counterpart.refersTo:
                return False
    return True
