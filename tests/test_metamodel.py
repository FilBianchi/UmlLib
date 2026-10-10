import unittest
import umltools as uml


class MetamodelTests(unittest.TestCase):
    def test_complete_classifier_inventory(self):
        self.assertEqual(len(uml.SPECIFICATIONS), 242)
        self.assertEqual(len(uml.ENUMERATIONS), 13)
        for name in uml.SPECIFICATIONS:
            self.assertTrue(issubclass(getattr(uml, name), uml.UmlElement))

    def test_multiple_inheritance_and_model_construction(self):
        model = uml.Model(name='Example')
        cls = uml.Class(name='Customer')
        model.packagedElement = [cls]
        self.assertIsInstance(cls, uml.Classifier)
        self.assertIsInstance(cls, uml.Namespace)
        self.assertEqual(model.packagedElement[0].name, 'Customer')

    def test_types_abstract_classes_and_unknown_properties(self):
        with self.assertRaises(TypeError):
            uml.Element()
        with self.assertRaises(TypeError):
            uml.Class(name=42)
        with self.assertRaises(AttributeError):
            uml.Class(typo='value')
        with self.assertRaises(TypeError):
            uml.Model(packagedElement=['invalid'])

    def test_semantics_never_silently_pass(self):
        cls = uml.Class(name='Example')
        self.assertIn(('constraint', 'Element.has_owner'), cls.validate())
        self.assertEqual(cls.qualifiedName, 'Example')


if __name__ == '__main__':
    unittest.main()
