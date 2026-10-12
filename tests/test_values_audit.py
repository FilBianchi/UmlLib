"""Independent boundary examples for Values and multiplicity contracts."""
import unittest
import Uml
from umltools.native import check, NativeNotImplemented
from umltools.expression_semantics import register_expression_facts
from semantic_cases import verifies


class ValuesCases(unittest.TestCase):
    @verifies('LiteralBoolean.booleanValue', 'LiteralInteger.integerValue', 'LiteralReal.realValue',
              'LiteralString.stringValue', 'LiteralUnlimitedNatural.unlimitedValue',
              'LiteralBoolean.isComputable', 'LiteralInteger.isComputable', 'LiteralReal.isComputable',
              'LiteralString.isComputable', 'LiteralUnlimitedNatural.isComputable', 'LiteralNull.isComputable', 'LiteralNull.isNull',
              'ValueSpecification.booleanValue', 'ValueSpecification.integerValue', 'ValueSpecification.realValue',
              'ValueSpecification.stringValue', 'ValueSpecification.unlimitedValue', 'ValueSpecification.isComputable', 'ValueSpecification.isNull')
    def test_literal_domains_and_undefined_cross_queries(self):
        for cls, name, value in ((Uml.LiteralBoolean, 'booleanValue', False),
                                 (Uml.LiteralInteger, 'integerValue', -4),
                                 (Uml.LiteralReal, 'realValue', 2.5),
                                 (Uml.LiteralString, 'stringValue', ''),
                                 (Uml.LiteralUnlimitedNatural, 'unlimitedValue', float('inf'))):
            literal = cls(value=value)
            self.assertEqual(getattr(literal, name)(), value)
            self.assertTrue(literal.isComputable())
            self.assertFalse(literal.isNull())
            for other in ('booleanValue', 'integerValue', 'realValue', 'stringValue', 'unlimitedValue'):
                if other != name: self.assertIsNone(getattr(literal, other)())
        literal = Uml.LiteralNull()
        self.assertTrue(literal.isNull())
        self.assertTrue(literal.isComputable())
        opaque = Uml.OpaqueExpression()
        self.assertFalse(opaque.isComputable())
        self.assertFalse(opaque.isNull())

    @verifies('MultiplicityElement.lowerBound', 'MultiplicityElement.upperBound', 'MultiplicityElement.lower',
              'MultiplicityElement.upper', 'MultiplicityElement.is', 'MultiplicityElement.isMultivalued',
              'MultiplicityElement.compatibleWith', 'MultiplicityElement.includesMultiplicity',
              'MultiplicityElement.upper_ge_lower', 'MultiplicityElement.lower_ge_0',
              'MultiplicityElement.lower_is_integer', 'MultiplicityElement.upper_is_unlimitedNatural',
              'MultiplicityElement-includesMultiplicity-pre', 'MultiplicityElement-isMultivalued-pre')
    def test_multiplicity_defaults_infinity_and_wrong_value_kinds(self):
        prop = Uml.Property()
        self.assertEqual((prop.lower, prop.upper), (1, 1))
        self.assertTrue(prop.uml_operation('MultiplicityElement', 'is', 1, 1))
        self.assertFalse(prop.isMultivalued())
        prop.lowerValue, prop.upperValue = Uml.LiteralInteger(value=0), Uml.LiteralUnlimitedNatural(value=float('inf'))
        other = Uml.Property(lowerValue=Uml.LiteralInteger(value=2), upperValue=Uml.LiteralUnlimitedNatural(value=3))
        self.assertTrue(prop.isMultivalued())
        self.assertTrue(prop.includesMultiplicity(other))
        self.assertTrue(other.compatibleWith(prop))
        self.assertFalse(prop.compatibleWith(other))
        self.assertTrue(check(prop, 'MultiplicityElement.upper_ge_lower'))
        prop.lowerValue.value = -1
        self.assertFalse(check(prop, 'MultiplicityElement.lower_ge_0'))
        prop.lowerValue.value = 4
        prop.upperValue.value = 3
        self.assertFalse(check(prop, 'MultiplicityElement.upper_ge_lower'))
        prop.lowerValue, prop.upperValue = Uml.LiteralString(value='x'), Uml.LiteralInteger(value=9)
        self.assertEqual((prop.lower, prop.upper), (1, 1))  # Explicit defaults in the source bodies.
        self.assertFalse(check(prop, 'MultiplicityElement.lower_is_integer'))
        self.assertFalse(check(prop, 'MultiplicityElement.upper_is_unlimitedNatural'))

    @verifies('MultiplicityElement.value_specification_no_side_effects', 'MultiplicityElement.value_specification_constant')
    def test_bounds_need_explicit_purity_and_constancy_for_foreign_expressions(self):
        expression = Uml.OpaqueExpression()
        prop = Uml.Property(lowerValue=expression)
        for name in ('value_specification_no_side_effects', 'value_specification_constant'):
            with self.assertRaises(NativeNotImplemented): check(prop, 'MultiplicityElement.' + name)
        register_expression_facts(expression, pure=True, constant=False)
        self.assertTrue(check(prop, 'MultiplicityElement.value_specification_no_side_effects'))
        self.assertFalse(check(prop, 'MultiplicityElement.value_specification_constant'))

    @verifies('StringExpression.operands', 'StringExpression.subexpressions', 'StringExpression.stringValue')
    def test_ordered_concatenation_and_exclusive_subexpressions(self):
        expression = Uml.StringExpression(operand=[Uml.LiteralString(value='a'), Uml.LiteralString(value='b')])
        self.assertEqual(expression.stringValue(), 'ab')
        self.assertTrue(check(expression, 'StringExpression.operands'))
        self.assertTrue(check(expression, 'StringExpression.subexpressions'))
        expression.operand.append(Uml.LiteralInteger(value=1))
        self.assertFalse(check(expression, 'StringExpression.operands'))
        with self.assertRaises(ValueError): expression.stringValue()
        expression.operand.clear()
        self.assertFalse(check(expression, 'StringExpression.subexpressions'))
        expression.subExpression.append(Uml.StringExpression(operand=[Uml.LiteralString(value='nested')]))
        self.assertEqual(expression.stringValue(), 'nested')
        self.assertTrue(check(expression, 'StringExpression.subexpressions'))
        expression.operand.append(Uml.LiteralString(value='ignored'))
        self.assertFalse(check(expression, 'StringExpression.subexpressions'))

    @verifies('OpaqueExpression.language_body_size', 'OpaqueExpression.one_return_result_parameter',
              'OpaqueExpression.only_in_or_return_parameters', 'OpaqueExpression.result',
              'OpaqueExpression.isIntegral', 'OpaqueExpression.isNonNegative', 'OpaqueExpression.isPositive', 'OpaqueExpression.value',
              'OpaqueExpression-isNonNegative-pre', 'OpaqueExpression-isPositive-pre', 'OpaqueExpression-value-pre')
    def test_opaque_source_bodies_and_preconditions_without_executing_languages(self):
        expression = Uml.OpaqueExpression(body=['text'])
        self.assertTrue(check(expression, 'OpaqueExpression.language_body_size'))
        expression.language.extend(['Python', 'OCL'])
        self.assertFalse(check(expression, 'OpaqueExpression.language_body_size'))
        self.assertFalse(expression.isIntegral())
        for name in ('isNonNegative', 'isPositive', 'value'):
            with self.assertRaises(ValueError): getattr(expression, name)()
        self.assertIsNone(expression.result)
        first, result = Uml.Parameter(), Uml.Parameter(direction=Uml.ParameterDirectionKind.return_)
        behavior = Uml.OpaqueBehavior(ownedParameter=[first, result])
        expression.behavior = behavior
        self.assertIs(expression.result, first)  # XMI explicitly derives first(), not a return-filter.
        self.assertTrue(check(expression, 'OpaqueExpression.one_return_result_parameter'))
        self.assertTrue(check(expression, 'OpaqueExpression.only_in_or_return_parameters'))
        first.isStream = True
        self.assertFalse(check(expression, 'OpaqueExpression.only_in_or_return_parameters'))
        first.isStream = False
        first.direction = Uml.ParameterDirectionKind.out
        self.assertFalse(check(expression, 'OpaqueExpression.only_in_or_return_parameters'))
        result.direction = Uml.ParameterDirectionKind.in_
        self.assertFalse(check(expression, 'OpaqueExpression.one_return_result_parameter'))

    @verifies('ValueSpecification.isCompatibleWith')
    def test_value_compatibility_requires_kind_and_type_conformance(self):
        base, subtype = Uml.Class(), Uml.Class()
        subtype.generalization.append(Uml.Generalization(general=base))
        actual, formal = Uml.LiteralInteger(type=subtype), Uml.LiteralInteger(type=base)
        self.assertTrue(actual.isCompatibleWith(formal))
        self.assertFalse(formal.isCompatibleWith(actual))
        self.assertFalse(actual.isCompatibleWith(Uml.LiteralString(type=base)))
        with self.assertRaises(ValueError): Uml.LiteralInteger().isCompatibleWith(formal)

    @verifies('Duration.no_expr_requires_observation', 'TimeExpression.no_expr_requires_observation',
              'DurationObservation.first_event_multiplicity', 'DurationConstraint.first_event_multiplicity',
              'DurationConstraint.has_one_or_two_constrainedElements', 'TimeConstraint.has_one_constrainedElement')
    def test_observation_kinds_and_one_or_two_events(self):
        for cls, correct, wrong, rule in ((Uml.Duration, Uml.DurationObservation, Uml.TimeObservation, 'Duration.no_expr_requires_observation'),
                                         (Uml.TimeExpression, Uml.TimeObservation, Uml.DurationObservation, 'TimeExpression.no_expr_requires_observation')):
            expression = cls()
            self.assertFalse(check(expression, rule))
            expression.observation.append(correct())
            self.assertTrue(check(expression, rule))
            expression.observation.clear()
            expression.observation.append(wrong())
            self.assertFalse(check(expression, rule))
            expression.expr = Uml.LiteralInteger(value=1)
            self.assertTrue(check(expression, rule))
        observation = Uml.DurationObservation(event=[Uml.OccurrenceSpecification()])
        self.assertTrue(check(observation, 'DurationObservation.first_event_multiplicity'))
        observation.event.append(Uml.OccurrenceSpecification())
        self.assertFalse(check(observation, 'DurationObservation.first_event_multiplicity'))
        observation.firstEvent = [True, False]
        self.assertTrue(check(observation, 'DurationObservation.first_event_multiplicity'))
        constraint = Uml.DurationConstraint()
        self.assertFalse(check(constraint, 'DurationConstraint.has_one_or_two_constrainedElements'))
        constraint.constrainedElement.append(Uml.Class())
        self.assertTrue(check(constraint, 'DurationConstraint.has_one_or_two_constrainedElements'))
        self.assertTrue(check(constraint, 'DurationConstraint.first_event_multiplicity'))
        constraint.constrainedElement.append(Uml.Class())
        self.assertFalse(check(constraint, 'DurationConstraint.first_event_multiplicity'))
        constraint.firstEvent = [True, False]
        self.assertTrue(check(constraint, 'DurationConstraint.first_event_multiplicity'))
        constraint.constrainedElement.append(Uml.Class())
        self.assertFalse(check(constraint, 'DurationConstraint.has_one_or_two_constrainedElements'))
        time = Uml.TimeConstraint(constrainedElement=[Uml.Class()])
        self.assertTrue(check(time, 'TimeConstraint.has_one_constrainedElement'))
        time.constrainedElement.append(Uml.Class())
        self.assertFalse(check(time, 'TimeConstraint.has_one_constrainedElement'))
