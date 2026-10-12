"""Static behavior contexts and language-independent value evidence."""
import unittest
import Uml
from umltools import ModelSession
from umltools.native import check, NativeNotImplemented
from semantic_cases import verifies


class CommonBehaviorCases(unittest.TestCase):
    def setUp(self):
        self.scope = ModelSession()
        self.scope.__enter__()

    def tearDown(self): self.scope.__exit__(None, None, None)

    @verifies('Behavior.context', 'Behavior.behavioredClassifier', 'Behavior-behavioredClassifier-spec',
              'Behavior.parameters_match', 'Behavior.most_one_behavior', 'Behavior.feature_of_context_classifier')
    def test_optional_specification_method_context_and_duplicate_implementations(self):
        behavior = Uml.OpaqueBehavior()
        self.assertIsNone(behavior.context)
        self.assertTrue(check(behavior, 'Behavior.feature_of_context_classifier'))
        classifier = Uml.Class(ownedBehavior=[behavior])
        self.assertIs(behavior.context, classifier)
        self.assertIs(behavior.behavioredClassifier(classifier), classifier)
        self.assertIsNone(behavior.behavioredClassifier(Uml.Package()))
        operation = Uml.Operation(ownedParameter=[Uml.Parameter()])
        classifier.ownedOperation.append(operation)
        behavior.specification = operation
        self.assertTrue(check(behavior, 'Behavior.feature_of_context_classifier'))
        self.assertFalse(check(behavior, 'Behavior.parameters_match'))
        behavior.ownedParameter.append(Uml.Parameter())
        self.assertTrue(check(behavior, 'Behavior.parameters_match'))
        self.assertTrue(check(behavior, 'Behavior.most_one_behavior'))
        duplicate = Uml.OpaqueBehavior(specification=operation)
        classifier.ownedBehavior.append(duplicate)
        self.assertFalse(check(behavior, 'Behavior.most_one_behavior'))
        duplicate.delete()
        self.assertTrue(check(behavior, 'Behavior.most_one_behavior'))
        behavior.specification = Uml.Operation()
        self.assertFalse(check(behavior, 'Behavior.feature_of_context_classifier'))

    @verifies('Behavior.context', 'Behavior.inputParameters', 'Behavior.outputParameters')
    def test_context_through_nested_behavior_and_parameter_directions(self):
        classifier, outer, inner = Uml.Class(), Uml.OpaqueBehavior(), Uml.OpaqueBehavior()
        classifier.ownedBehavior.append(outer)
        outer.ownedBehavior.append(inner)
        self.assertIs(inner.context, classifier)
        nested = Uml.OpaqueBehavior()
        classifier.nestedClassifier.append(nested)
        self.assertIsNone(nested.context)
        params = [Uml.Parameter(direction=d) for d in (Uml.ParameterDirectionKind.in_, Uml.ParameterDirectionKind.inout,
                                                     Uml.ParameterDirectionKind.out, Uml.ParameterDirectionKind.return_)]
        inner.ownedParameter = params
        self.assertEqual(inner.inputParameters(), params[:2])
        self.assertEqual(inner.outputParameters(), params[1:])

    @verifies('FunctionBehavior.one_output_parameter', 'FunctionBehavior.types_of_parameters', 'FunctionBehavior.hasAllDataTypeAttributes')
    def test_function_datatype_graphs_cycles_and_exact_parameter_type(self):
        scalar, aggregate = Uml.PrimitiveType(), Uml.DataType()
        aggregate.ownedAttribute.append(Uml.Property(type=scalar))
        function = Uml.FunctionBehavior(ownedParameter=[Uml.Parameter(type=aggregate)])
        self.assertFalse(check(function, 'FunctionBehavior.one_output_parameter'))
        function.ownedParameter[0].direction = Uml.ParameterDirectionKind.return_
        self.assertTrue(check(function, 'FunctionBehavior.one_output_parameter'))
        self.assertTrue(check(function, 'FunctionBehavior.types_of_parameters'))
        aggregate.ownedAttribute.append(Uml.Property(type=aggregate))
        self.assertTrue(function.hasAllDataTypeAttributes(aggregate))
        aggregate.ownedAttribute.append(Uml.Property(type=Uml.Class()))
        self.assertFalse(function.hasAllDataTypeAttributes(aggregate))
        function.ownedParameter[0].type = scalar
        self.assertFalse(check(function, 'FunctionBehavior.types_of_parameters'))  # XMI uses isTypeOf, not isKindOf.

    @verifies('TimeEvent.when_non_negative', 'Trigger.trigger_with_ports')
    def test_time_literal_evidence_unknown_observations_and_message_event_ports(self):
        expression = Uml.TimeExpression(expr=Uml.LiteralInteger(value=0))
        event = Uml.TimeEvent(when=expression)
        self.assertTrue(check(event, 'TimeEvent.when_non_negative'))
        expression.expr.value = -1
        self.assertFalse(check(event, 'TimeEvent.when_non_negative'))
        expression.expr = Uml.LiteralString(value='tomorrow')
        self.assertFalse(check(event, 'TimeEvent.when_non_negative'))
        expression.expr = Uml.OpaqueExpression(body=['now'], language=['custom'])
        with self.assertRaises(NativeNotImplemented): check(event, 'TimeEvent.when_non_negative')
        self.assertIn(('unsupported constraint', 'TimeEvent.when_non_negative'), event.validate())
        trigger = Uml.Trigger(event=event, port=[Uml.Port()])
        self.assertFalse(check(trigger, 'Trigger.trigger_with_ports'))
        trigger.event = Uml.SignalEvent(signal=Uml.Signal())
        self.assertTrue(check(trigger, 'Trigger.trigger_with_ports'))
