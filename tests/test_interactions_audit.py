"""Interaction boundary, signature, ordering and contextual evidence scenarios."""
import unittest
import Uml
from umltools import ModelSession
from umltools.native import check, NativeNotImplemented
from umltools.expression_semantics import register_expression_facts
from semantic_cases import verifies


class InteractionCases(unittest.TestCase):
    def setUp(self):
        self.session = ModelSession()
        self.session.__enter__()

    def tearDown(self): self.session.__exit__(None, None, None)

    def rules(self, obj, *names, expected=True):
        for name in names:
            with self.subTest(rule=name): self.assertEqual(check(obj, name), expected)

    @verifies('Message.messageKind', 'Message-messageKind', 'Message.isDistinguishableFrom',
              'MessageEnd.oppositeEnd', 'MessageEnd.isSend', 'MessageEnd.isReceive', 'MessageEnd.enclosingFragment',
              'MessageEnd-oppositeEnd-pre', 'MessageEnd-isSend-pre', 'MessageEnd-isReceive-pre')
    def test_message_kinds_end_navigation_and_preconditions(self):
        m, send, receive = Uml.Message(), Uml.MessageOccurrenceSpecification(), Uml.MessageOccurrenceSpecification()
        self.assertEqual(m.messageKind, Uml.MessageKind.unknown)
        for name in ('oppositeEnd', 'isSend', 'isReceive'):
            with self.assertRaises(ValueError): getattr(send, name)()
        m.sendEvent = send
        self.assertEqual(m.messageKind, Uml.MessageKind.lost)
        self.assertEqual(send.oppositeEnd(), [])
        m.receiveEvent = receive
        self.assertEqual(m.messageKind, Uml.MessageKind.complete)
        self.assertEqual(send.oppositeEnd(), [receive])
        self.assertTrue(send.isSend())
        self.assertFalse(send.isReceive())
        self.assertTrue(receive.isReceive())
        parent = Uml.Interaction(fragment=[send, receive], message=[m])
        self.assertEqual(send.enclosingFragment(), [parent])
        self.assertTrue(m.isDistinguishableFrom(Uml.Message(), parent))
        m.sendEvent = None
        self.assertEqual(m.messageKind, Uml.MessageKind.found)
        self.assertIsNone(send.message)

    @verifies('Gate.isOutsideCF', 'Gate.isInsideCF', 'Gate.getName', 'Gate.matches', 'Gate.getOperand',
              'Gate.inside_cf_matched', 'Gate.outside_cf_matched', 'Gate.outside_cf_gate_distinguishable',
              'Gate.inside_cf_gate_distinguishable', 'Message.cannot_cross_boundaries')
    def test_alt_gate_matches_per_operand_and_distinct_boundary_sides(self):
        outside = Uml.Gate()
        ops = [Uml.InteractionOperand(), Uml.InteractionOperand()]
        cf = Uml.CombinedFragment(interactionOperator=Uml.InteractionOperatorKind.alt, operand=ops, cfragmentGate=[outside])
        external = Uml.MessageOccurrenceSpecification()
        parent = Uml.Interaction(fragment=[cf, external])
        message = Uml.Message(name='request', sendEvent=external, receiveEvent=outside)
        parent.message.append(message)
        insiders = []
        for op in ops:
            inside, occurrence = Uml.Gate(), Uml.MessageOccurrenceSpecification()
            cf.cfragmentGate.append(inside)
            op.fragment.append(occurrence)
            parent.message.append(Uml.Message(name='request', sendEvent=inside, receiveEvent=occurrence))
            insiders.append(inside)
            self.assertTrue(inside.isInsideCF())
            self.assertFalse(inside.isOutsideCF())
            self.assertIs(inside.getOperand(), op)
            self.assertEqual(inside.enclosingFragment(), [cf])
            self.assertEqual(inside.getName(), 'in_request')
            self.assertTrue(inside.matches(outside))
            self.rules(inside, 'Gate.inside_cf_matched', 'Gate.inside_cf_gate_distinguishable')
        self.assertTrue(outside.isOutsideCF())
        self.assertFalse(outside.isInsideCF())
        self.assertIsNone(outside.getOperand())
        self.assertEqual(outside.enclosingFragment(), [parent])
        self.assertEqual(outside.getName(), 'in_request')
        self.rules(outside, 'Gate.outside_cf_matched', 'Gate.outside_cf_gate_distinguishable')
        self.rules(message, 'Message.cannot_cross_boundaries')
        insiders[1].message.name = 'different'
        self.rules(outside, 'Gate.outside_cf_matched', expected=False)
        self.assertFalse(insiders[1].matches(outside))
        direct = Uml.Message(sendEvent=external, receiveEvent=ops[0].fragment[0])
        self.rules(direct, 'Message.cannot_cross_boundaries', expected=False)

    @verifies('Gate.isActual', 'Gate.isFormal', 'Gate.isDistinguishableFrom', 'Gate.actual_gate_matched',
              'Gate.formal_gate_distinguishable', 'Gate.actual_gate_distinguishable', 'InteractionUse.gates_match')
    def test_actual_formal_gate_names_signatures_and_duplicate_matches(self):
        actual, formal = Uml.Gate(), Uml.Gate()
        referred = Uml.Interaction(formalGate=[formal])
        use = Uml.InteractionUse(refersTo=referred, actualGate=[actual])
        parent = Uml.Interaction(fragment=[use])
        m = Uml.Message(name='call', sendEvent=actual, receiveEvent=Uml.MessageOccurrenceSpecification())
        n = Uml.Message(name='call', sendEvent=Uml.MessageOccurrenceSpecification(), receiveEvent=formal)
        self.assertTrue(actual.isActual())
        self.assertTrue(formal.isFormal())
        self.assertFalse(actual.isFormal())
        self.assertFalse(formal.isActual())
        self.assertEqual(actual.enclosingFragment(), [parent])
        self.assertEqual(formal.enclosingFragment(), [referred])
        self.assertEqual(actual.getName(), 'out_call')
        self.assertEqual(formal.getName(), 'out_call')
        self.assertTrue(actual.isDistinguishableFrom(formal, parent))
        self.rules(actual, 'Gate.actual_gate_matched', 'Gate.actual_gate_distinguishable')
        self.rules(formal, 'Gate.formal_gate_distinguishable')
        self.rules(use, 'InteractionUse.gates_match')
        n.signature = Uml.Operation()
        self.assertFalse(actual.matches(formal))
        self.rules(use, 'InteractionUse.gates_match', expected=False)
        n.signature = None
        duplicate = Uml.Gate(name='out_call')
        referred.formalGate.append(duplicate)
        Uml.Message(name='call', receiveEvent=duplicate)
        self.rules(formal, 'Gate.formal_gate_distinguishable', expected=False)
        self.rules(actual, 'Gate.actual_gate_matched', expected=False)
        second = Uml.Gate(name='out_call')
        use.actualGate.append(second)
        Uml.Message(name='call', sendEvent=second)
        self.rules(actual, 'Gate.actual_gate_distinguishable', expected=False)
        detached = Uml.Gate(name='explicit')
        self.assertEqual(detached.getName(), 'explicit')
        self.assertFalse(detached.isInsideCF())
        self.assertFalse(detached.isOutsideCF())
        self.assertEqual(detached.enclosingFragment(), [])
        self.assertIsNone(detached.getOperand())

    @verifies('CombinedFragment.break', 'CombinedFragment.consider_and_ignore', 'CombinedFragment.opt_loop_break_neg',
              'ConsiderIgnoreFragment.consider_or_ignore', 'ConsiderIgnoreFragment.type', 'Interaction.not_contained')
    def test_combined_fragment_operators_coverage_and_signature_kinds(self):
        lines = [Uml.Lifeline(), Uml.Lifeline()]
        parent = Uml.Interaction(lifeline=lines, covered=lines)
        cf = Uml.CombinedFragment(interactionOperator=Uml.InteractionOperatorKind.break_, covered=lines, operand=[Uml.InteractionOperand()])
        parent.fragment.append(cf)
        self.rules(parent, 'Interaction.not_contained')
        self.rules(cf, 'CombinedFragment.break', 'CombinedFragment.opt_loop_break_neg', 'CombinedFragment.consider_and_ignore')
        cf.covered.pop()
        self.rules(cf, 'CombinedFragment.break', expected=False)
        cf.operand.append(Uml.InteractionOperand())
        self.rules(cf, 'CombinedFragment.opt_loop_break_neg', expected=False)
        cf.interactionOperator = Uml.InteractionOperatorKind.consider
        self.rules(cf, 'CombinedFragment.consider_and_ignore', expected=False)
        special = Uml.ConsiderIgnoreFragment(interactionOperator=Uml.InteractionOperatorKind.ignore, message=[Uml.Signal(), Uml.Operation()])
        self.rules(special, 'ConsiderIgnoreFragment.consider_or_ignore', 'ConsiderIgnoreFragment.type', 'CombinedFragment.consider_and_ignore')
        special.message.append(Uml.Class())
        self.rules(special, 'ConsiderIgnoreFragment.type', expected=False)
        special.interactionOperator = Uml.InteractionOperatorKind.alt
        self.rules(special, 'ConsiderIgnoreFragment.consider_or_ignore', expected=False)
        child = Uml.Interaction()
        parent.fragment.append(child)
        self.rules(child, 'Interaction.not_contained', expected=False)

    @verifies('ExecutionSpecification.same_lifeline', 'ActionExecutionSpecification.action_referenced',
              'DestructionOccurrenceSpecification.no_occurrence_specifications_below',
              'Message.sending_receiving_message_event', 'GeneralOrdering.irreflexive_transitive_closure')
    def test_nested_event_order_execution_ownership_and_ordering_cycles(self):
        line = Uml.Lifeline()
        start, finish = Uml.ExecutionOccurrenceSpecification(covered=line), Uml.ExecutionOccurrenceSpecification(covered=line)
        action = Uml.OpaqueAction()
        execution = Uml.ActionExecutionSpecification(start=start, finish=finish, action=action)
        operand = Uml.InteractionOperand(fragment=[start, execution, finish])
        cf = Uml.CombinedFragment(operand=[operand])
        receive = Uml.MessageOccurrenceSpecification(covered=line)
        send = Uml.MessageOccurrenceSpecification(covered=line)
        operand.fragment.append(send)
        parent = Uml.Interaction(lifeline=[line], fragment=[cf, receive], action=[action])
        message = Uml.Message(sendEvent=send, receiveEvent=receive)
        self.rules(execution, 'ExecutionSpecification.same_lifeline', 'ActionExecutionSpecification.action_referenced')
        self.rules(message, 'Message.sending_receiving_message_event')
        parent.fragment.reverse()
        self.rules(message, 'Message.sending_receiving_message_event', expected=False)
        finish.covered = Uml.Lifeline()
        self.rules(execution, 'ExecutionSpecification.same_lifeline', expected=False)
        parent.action.remove(action)
        self.rules(execution, 'ActionExecutionSpecification.action_referenced', expected=False)
        destroy = Uml.DestructionOccurrenceSpecification(covered=line)
        operand.fragment.append(destroy)
        self.rules(destroy, 'DestructionOccurrenceSpecification.no_occurrence_specifications_below')
        operand.fragment.append(Uml.OccurrenceSpecification(covered=line))
        self.rules(destroy, 'DestructionOccurrenceSpecification.no_occurrence_specifications_below', expected=False)
        a, b, c = [Uml.OccurrenceSpecification() for _ in range(3)]
        first = Uml.GeneralOrdering(before=a, after=b)
        Uml.GeneralOrdering(before=b, after=c)
        self.rules(first, 'GeneralOrdering.irreflexive_transitive_closure')
        Uml.GeneralOrdering(before=c, after=a)
        self.rules(first, 'GeneralOrdering.irreflexive_transitive_closure', expected=False)

    @verifies('Continuation.first_or_last_interaction_fragment', 'Continuation.same_name', 'Continuation.global')
    def test_continuations_common_lifelines_and_operand_end_positions(self):
        role = Uml.Property()
        cls = Uml.Class(ownedAttribute=[role])
        first, second = Uml.Lifeline(represents=role), Uml.Lifeline(represents=role)
        continuations = []
        for line in (first, second):
            continuation = Uml.Continuation(name='resume', covered=[line])
            op = Uml.InteractionOperand(covered=[line], fragment=[continuation])
            interaction = Uml.Interaction(lifeline=[line], fragment=[Uml.CombinedFragment(operand=[op])])
            cls.ownedBehavior.append(interaction)
            continuations.append(continuation)
            self.rules(continuation, 'Continuation.first_or_last_interaction_fragment', 'Continuation.global', 'Continuation.same_name')
        second.represents = Uml.Property()
        self.rules(continuations[0], 'Continuation.same_name', expected=False)
        op = continuations[0].enclosingOperand
        op.fragment.insert(0, Uml.StateInvariant())
        op.fragment.append(Uml.StateInvariant())
        self.rules(continuations[0], 'Continuation.first_or_last_interaction_fragment', expected=False)
        op.covered.append(Uml.Lifeline())
        self.rules(continuations[0], 'Continuation.global', expected=False)

    @verifies('InteractionConstraint.minint_maxint', 'InteractionConstraint.minint_non_negative',
              'InteractionConstraint.maxint_positive', 'InteractionConstraint.maxint_greater_equal_minint')
    def test_loop_bounds_invalid_literals_and_missing_numeric_evaluator(self):
        guard = Uml.InteractionConstraint(minint=Uml.LiteralInteger(value=0), maxint=Uml.LiteralInteger(value=2))
        op = Uml.InteractionOperand(guard=guard)
        cf = Uml.CombinedFragment(interactionOperator=Uml.InteractionOperatorKind.loop, operand=[op])
        self.rules(guard, 'InteractionConstraint.minint_maxint', 'InteractionConstraint.minint_non_negative',
                   'InteractionConstraint.maxint_positive', 'InteractionConstraint.maxint_greater_equal_minint')
        guard.minint.value = -1
        self.rules(guard, 'InteractionConstraint.minint_non_negative', expected=False)
        guard.minint.value, guard.maxint.value = 3, 2
        self.rules(guard, 'InteractionConstraint.maxint_greater_equal_minint', expected=False)
        guard.maxint.value = 0
        self.rules(guard, 'InteractionConstraint.maxint_positive', expected=False)
        cf.interactionOperator = Uml.InteractionOperatorKind.opt
        self.rules(guard, 'InteractionConstraint.minint_maxint', expected=False)
        guard.maxint = Uml.OpaqueExpression(body=['limit'], language=['custom'])
        with self.assertRaises(NativeNotImplemented): check(guard, 'InteractionConstraint.maxint_positive')
        self.assertIn(('unsupported constraint', 'InteractionConstraint.maxint_positive'), guard.validate())
        guard.maxint = Uml.LiteralString(value='2')
        with self.assertRaises(ValueError): check(guard, 'InteractionConstraint.maxint_positive')

    @verifies('Lifeline.selector_specified', 'Lifeline.selector_int_or_string', 'Lifeline.same_classifier',
              'InteractionUse.all_lifelines', 'Lifeline.interaction_uses_share_lifeline')
    def test_lifeline_selectors_common_use_coverage_and_context(self):
        role = Uml.Property(upperValue=Uml.LiteralUnlimitedNatural(value=3))
        cls = Uml.Class(ownedAttribute=[role])
        lines = [Uml.Lifeline(represents=role, selector=Uml.LiteralInteger(value=1)) for _ in range(3)]
        parent, first, second = [Uml.Interaction(lifeline=[l]) for l in lines]
        cls.ownedBehavior.extend([parent, first, second])
        use = Uml.InteractionUse(refersTo=first, covered=[lines[0]])
        peer = Uml.InteractionUse(refersTo=second)
        parent.fragment.extend([use, peer])
        self.rules(lines[0], 'Lifeline.selector_specified', 'Lifeline.selector_int_or_string', 'Lifeline.same_classifier')
        self.rules(use, 'InteractionUse.all_lifelines')
        self.rules(lines[1], 'Lifeline.interaction_uses_share_lifeline')
        use.covered.clear()
        self.rules(use, 'InteractionUse.all_lifelines', expected=False)
        lines[0].selector.value = 2
        self.rules(lines[1], 'Lifeline.interaction_uses_share_lifeline', expected=False)
        lines[0].selector = Uml.LiteralBoolean()
        self.rules(lines[0], 'Lifeline.selector_int_or_string', expected=False)
        lines[0].selector = None
        self.rules(lines[0], 'Lifeline.selector_specified', expected=False)
        lines[0].represents = Uml.Property()
        self.rules(lines[0], 'Lifeline.same_classifier', expected=False)

    @verifies('Message.signature_is_signal', 'Message.signature_refer_to', 'Message.signature_is_operation_request',
              'Message.signature_is_operation_reply', 'Message.occurrence_specifications')
    def test_message_signature_directions_wildcards_and_connector_roles(self):
        base = Uml.Class()
        child = Uml.Class(generalization=[Uml.Generalization(general=base)])
        signal = Uml.Signal(name='notice', ownedAttribute=[Uml.Property(type=base)])
        m = Uml.Message(name='notice', signature=signal, messageSort=Uml.MessageSort.asynchSignal,
                        argument=[Uml.LiteralInteger(type=child)])
        self.rules(m, 'Message.signature_is_signal', 'Message.signature_refer_to')
        m.argument[0].type = Uml.Class()
        self.rules(m, 'Message.signature_is_signal', expected=False)
        m.argument = [Uml.Expression()]
        self.rules(m, 'Message.signature_is_signal')
        operation = Uml.Operation(name='call', ownedParameter=[Uml.Parameter(type=base),
                          Uml.Parameter(type=base, direction=Uml.ParameterDirectionKind.return_)])
        m.signature, m.name, m.messageSort = operation, 'call', Uml.MessageSort.synchCall
        m.argument = [Uml.LiteralInteger(type=child)]
        self.rules(m, 'Message.signature_is_operation_request', 'Message.signature_refer_to')
        m.argument.append(Uml.Expression())
        self.rules(m, 'Message.signature_is_operation_request', expected=False)
        m.messageSort = Uml.MessageSort.reply
        m.argument = [Uml.Expression(operand=[Uml.LiteralInteger(type=child)])]
        self.rules(m, 'Message.signature_is_operation_reply')
        m.argument[0].operand[0].type = Uml.Class()
        self.rules(m, 'Message.signature_is_operation_reply', expected=False)
        m.name = 'wrong'
        self.rules(m, 'Message.signature_refer_to', expected=False)
        roles = [Uml.Property(), Uml.Property()]
        lines = [Uml.Lifeline(represents=r) for r in roles]
        m.sendEvent, m.receiveEvent = [Uml.MessageOccurrenceSpecification(covered=l) for l in lines]
        m.connector = Uml.Connector(end=[Uml.ConnectorEnd(role=r) for r in roles])
        self.rules(m, 'Message.occurrence_specifications')
        m.connector.end[1].role = Uml.Property()
        self.rules(m, 'Message.occurrence_specifications', expected=False)

    @verifies('InteractionUse.arguments_are_constants', 'InteractionUse.arguments_correspond_to_parameters',
              'InteractionUse.returnValueRecipient_coverage', 'InteractionUse.returnValue_type_recipient_correspondence',
              'Message.arguments', 'InteractionConstraint.dynamic_variables', 'InteractionConstraint.global_data',
              'InteractionOperand.guard_contain_references', 'InteractionOperand.guard_directly_prior')
    def test_arguments_guard_references_and_return_recipient_evidence(self):
        t = Uml.Class()
        attribute = Uml.Property(type=t)
        cls = Uml.Class(ownedAttribute=[attribute])
        role = Uml.Property(type=cls)
        line = Uml.Lifeline(represents=role)
        referred = Uml.Interaction(ownedParameter=[Uml.Parameter(type=t)])
        use = Uml.InteractionUse(refersTo=referred, covered=[line], argument=[Uml.LiteralInteger(type=t)],
                                 returnValue=Uml.LiteralInteger(type=t), returnValueRecipient=attribute)
        expression = Uml.OpaqueExpression(type=t, body=['attribute'], language=['custom'])
        guard = Uml.InteractionConstraint(specification=expression)
        operand = Uml.InteractionOperand(covered=[line], guard=guard)
        parent = Uml.Interaction(lifeline=[line], fragment=[use, Uml.CombinedFragment(operand=[operand])])
        cls.ownedBehavior.append(parent)
        message = Uml.Message(argument=[Uml.LiteralInteger()])
        parent.message.append(message)
        self.rules(use, 'InteractionUse.arguments_are_constants', 'InteractionUse.arguments_correspond_to_parameters',
                   'InteractionUse.returnValueRecipient_coverage', 'InteractionUse.returnValue_type_recipient_correspondence')
        self.rules(message, 'Message.arguments')
        with self.assertRaises(NativeNotImplemented): check(guard, 'InteractionConstraint.dynamic_variables')
        register_expression_facts(expression, references=[attribute], constant=False)
        self.rules(guard, 'InteractionConstraint.dynamic_variables', 'InteractionConstraint.global_data')
        self.rules(operand, 'InteractionOperand.guard_contain_references', 'InteractionOperand.guard_directly_prior')
        foreign = Uml.Property()
        register_expression_facts(expression, references=[foreign], constant=False)
        self.rules(operand, 'InteractionOperand.guard_contain_references', expected=False)
        self.rules(guard, 'InteractionConstraint.dynamic_variables', 'InteractionConstraint.global_data', expected=False)
        use.argument = [Uml.OpaqueExpression(type=t)]
        with self.assertRaises(NativeNotImplemented): check(use, 'InteractionUse.arguments_are_constants')
        register_expression_facts(use.argument[0], constant=False, references=[foreign])
        self.rules(use, 'InteractionUse.arguments_are_constants', expected=False)
        use.argument[0].type = Uml.Class()
        self.rules(use, 'InteractionUse.arguments_correspond_to_parameters', expected=False)
        use.returnValueRecipient = foreign
        self.rules(use, 'InteractionUse.returnValueRecipient_coverage', 'InteractionUse.returnValue_type_recipient_correspondence', expected=False)

    @verifies('Gate.isInsideCF', 'Gate.isOutsideCF', 'Gate.getOperand', 'Gate.matches')
    def test_gate_to_gate_nested_fragment_context_and_matching_direction(self):
        outer_gate, inner_gate = Uml.Gate(name='port'), Uml.Gate(name='port')
        child = Uml.CombinedFragment(cfragmentGate=[inner_gate])
        op = Uml.InteractionOperand(fragment=[child])
        outer = Uml.CombinedFragment(operand=[op], cfragmentGate=[outer_gate])
        parent = Uml.Interaction(fragment=[outer])
        Uml.Message(name='transfer', sendEvent=outer_gate, receiveEvent=inner_gate)
        self.assertTrue(outer_gate.isInsideCF())
        self.assertFalse(outer_gate.isOutsideCF())
        self.assertFalse(inner_gate.isOutsideCF())
        self.assertIs(outer_gate.getOperand(), op)
        self.assertIsNone(inner_gate.getOperand())
        sibling_gate = Uml.Gate()
        op.fragment.append(Uml.CombinedFragment(cfragmentGate=[sibling_gate]))
        Uml.Message(sendEvent=inner_gate, receiveEvent=sibling_gate)
        self.assertTrue(inner_gate.isOutsideCF())
        self.assertTrue(sibling_gate.isOutsideCF())
        a, b = Uml.Gate(name='same'), Uml.Gate(name='same')
        ma, mb = Uml.Message(name='event', sendEvent=a), Uml.Message(name='event', receiveEvent=b)
        self.assertTrue(a.matches(b))
        mb.messageSort = Uml.MessageSort.asynchSignal
        self.assertFalse(a.matches(b))
        mb.messageSort = ma.messageSort
        mb.receiveEvent, mb.sendEvent = None, b
        self.assertFalse(a.matches(b))

    @verifies('Message.signature_is_operation_reply')
    def test_reply_source_only_checks_the_first_expression_operand(self):
        t = Uml.Class()
        op = Uml.Operation(ownedParameter=[Uml.Parameter(type=t, direction=Uml.ParameterDirectionKind.return_)])
        message = Uml.Message(signature=op, messageSort=Uml.MessageSort.reply, argument=[Uml.LiteralInteger(type=Uml.Class())])
        # The source implication is vacuous for a direct literal. It does not
        # prove the broader type-correspondence requirement in the description.
        self.rules(message, 'Message.signature_is_operation_reply')
        message.argument = [Uml.Expression(operand=[Uml.LiteralInteger(type=Uml.Class())])]
        self.rules(message, 'Message.signature_is_operation_reply', expected=False)
