import unittest
import UML
import umltools


class ExplicitModuleTests(unittest.TestCase):
    def test_all_classifiers_are_declared(self):
        self.assertEqual(len(UML.__all__), 255)
        for name in umltools.SPECIFICATIONS:
            self.assertEqual(getattr(UML, name).__module__, f'Uml.{umltools.SPECIFICATIONS[name].package}._{name}')

    def test_create_typed_model(self):
        customer = UML.Class(name='Customer')
        customer.ownedAttribute = [UML.Property(name='id')]
        model = UML.Model(name='Shop', packagedElement=[customer])
        self.assertIsInstance(model.packagedElement[0], UML.Classifier)
        self.assertIn('ownedAttribute', UML.Class.__annotations__)
        with self.assertRaises(TypeError):
            customer.visibility = 'public'
        customer.visibility = UML.VisibilityKind.public

    def test_python_keyword_aliases(self):
        prop = UML.Property()
        owner = UML.Class()
        prop.class_ = owner
        self.assertIs(prop.class_, owner)
        self.assertEqual(UML.InteractionOperatorKind.break_.value, 'break')
