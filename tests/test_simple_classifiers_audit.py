"""SimpleClassifiers examples, including signal/reception signature changes."""
import unittest
import Uml
from umltools.native import check
from semantic_cases import verifies


class SimpleClassifierCases(unittest.TestCase):
    @verifies('BehavioredClassifier.class_behavior')
    def test_classifier_behavior_must_not_implement_a_behavioral_feature(self):
        classifier, behavior = Uml.Class(), Uml.OpaqueBehavior()
        classifier.classifierBehavior = behavior
        self.assertEqual(list(classifier.ownedBehavior), [behavior])
        self.assertEqual(list(behavior.ownedBehavior), [])
        self.assertTrue(check(classifier, 'BehavioredClassifier.class_behavior'))
        behavior.specification = Uml.Operation()
        self.assertFalse(check(classifier, 'BehavioredClassifier.class_behavior'))
        classifier.ownedBehavior.remove(behavior)
        self.assertIsNone(classifier.classifierBehavior)

    @verifies('Enumeration.immutable', 'EnumerationLiteral.classifier', 'EnumerationLiteral-classifier')
    def test_enumeration_literals_and_readonly_attributes(self):
        literal = Uml.EnumerationLiteral(name='Ready')
        enumeration = Uml.Enumeration(ownedLiteral=[literal])
        self.assertIs(literal.classifier, enumeration)
        attribute = Uml.Property(isReadOnly=True)
        enumeration.ownedAttribute.append(attribute)
        self.assertTrue(check(enumeration, 'Enumeration.immutable'))
        attribute.isReadOnly = False
        self.assertFalse(check(enumeration, 'Enumeration.immutable'))

    @verifies('Interface.visibility')
    def test_interface_features_have_public_visibility(self):
        interface = Uml.Interface(ownedOperation=[Uml.Operation(visibility=Uml.VisibilityKind.public)])
        self.assertTrue(check(interface, 'Interface.visibility'))
        interface.ownedOperation[0].visibility = Uml.VisibilityKind.private
        self.assertFalse(check(interface, 'Interface.visibility'))
        interface.ownedOperation[0].visibility = None
        self.assertFalse(check(interface, 'Interface.visibility'))

    @verifies('Reception.same_name_as_signal', 'Reception.same_structure_as_signal')
    def test_reception_matches_signal_attribute_order_names_types_and_bounds(self):
        type_ = Uml.PrimitiveType(name='Integer')
        signal = Uml.Signal(name='Notify', ownedAttribute=[Uml.Property(name='a', type=type_), Uml.Property(name='b', type=type_)])
        a, b = Uml.Parameter(name='a', type=type_), Uml.Parameter(name='b', type=type_)
        reception = Uml.Reception(name='Notify', signal=signal, ownedParameter=[a, b])
        self.assertTrue(check(reception, 'Reception.same_name_as_signal'))
        self.assertTrue(check(reception, 'Reception.same_structure_as_signal'))
        reception.name = 'Other'
        self.assertFalse(check(reception, 'Reception.same_name_as_signal'))
        reception.ownedParameter.reverse()
        self.assertFalse(check(reception, 'Reception.same_structure_as_signal'))
        reception.ownedParameter.reverse()
        a.direction = Uml.ParameterDirectionKind.out
        self.assertFalse(check(reception, 'Reception.same_structure_as_signal'))
        a.direction = Uml.ParameterDirectionKind.in_
        a.upperValue = Uml.LiteralUnlimitedNatural(value=2)
        self.assertFalse(check(reception, 'Reception.same_structure_as_signal'))
