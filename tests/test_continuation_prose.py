import unittest
import Uml251 as U
from umltools import ModelSession
from umltools.native import check, NativeNotImplemented
from umltools.static_requirements import check_static
from semantic_cases import verifies


class ContinuationProseCases(unittest.TestCase):
    def setUp(self):
        self.session=ModelSession();self.session.__enter__()
        self.addCleanup(self.session.__exit__,None,None,None)

    def continuation(self, interaction, role, selector=None):
        line=U.Lifeline(represents=role,selector=selector)
        continuation=U.Continuation(name='resume',covered=[line])
        operand=U.InteractionOperand(fragment=[continuation],covered=[line])
        interaction.lifeline.append(line)
        interaction.fragment.append(U.CombinedFragment(operand=[operand]))
        return continuation,line

    @verifies('prose:Continuation.same_context_lifelines')
    def test_nested_behavior_peer_census_and_different_context(self):
        role=U.Property();context=U.Class(ownedAttribute=[role])
        parent=U.Interaction();nested=U.Interaction()
        context.ownedBehavior.append(parent);parent.ownedBehavior.append(nested)
        first,line1=self.continuation(parent,role)
        second,line2=self.continuation(nested,role)
        self.assertIs(nested.context,context)
        self.assertTrue(check_static(first,'prose:Continuation.same_context_lifelines'))
        line2.represents=U.Property()
        self.assertTrue(check(first,'Continuation.same_name'))
        self.assertFalse(check_static(first,'prose:Continuation.same_context_lifelines'))
        self.assertIn(('constraint','prose:Continuation.same_context_lifelines'),first.validate())
        context2=U.Class();context2.ownedBehavior.append(U.Interaction())
        # Transfer the peer to a different context; it must no longer participate.
        parent.ownedBehavior.remove(nested);context2.ownedBehavior.append(nested)
        self.assertTrue(check_static(first,'prose:Continuation.same_context_lifelines'))

    @verifies('Continuation.same_name','prose:Continuation.same_context_lifelines')
    def test_nonliteral_selectors_unknown_not_equal_and_literal_counterexamples(self):
        role=U.Property();context=U.Class(ownedAttribute=[role])
        a,b=U.Interaction(),U.Interaction();context.ownedBehavior.extend([a,b])
        first,line1=self.continuation(a,role,U.OpaqueExpression(body=['one']))
        second,line2=self.continuation(b,role,U.OpaqueExpression(body=['two']))
        with self.assertRaises(NativeNotImplemented):check(first,'Continuation.same_name')
        self.assertIn(('unsupported constraint','prose:Continuation.same_context_lifelines'),first.validate())
        line1.selector=U.LiteralInteger(value=1);line2.selector=U.LiteralInteger(value=1)
        self.assertTrue(check_static(first,'prose:Continuation.same_context_lifelines'))
        line2.selector.value=2
        self.assertFalse(check_static(first,'prose:Continuation.same_context_lifelines'))


if __name__=='__main__':unittest.main()
