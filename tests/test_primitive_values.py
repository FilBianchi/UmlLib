import unittest
from decimal import Decimal
import Uml
from umltools import ModelSession,DeletedElementError
from umltools.native import NativeNotImplemented
from umltools.primitive_values import PrimitiveValue,register_primitive_codec,unregister_primitive_codec
from umltools.profile_values import register_profile_constraint
from umltools.stereotypes import apply_profile,apply_stereotype,applications
from umltools.xmi import loads,dumps,XmiUnsupportedError,UML_NS,XMI_NS
from semantic_cases import verifies


class PrimitiveCases(unittest.TestCase):
    def setUp(self):
        from test_stereotype_applications import StereotypeCases
        self.session=ModelSession();self.session.__enter__()
        self.profile=Uml.Profile(name='Domain');self.metamodel=Uml.Model(name='UML')
        self.model=Uml.Model(name='Model',packagedElement=[Uml.Class(name='C')])
        self.stereo,self.bases=StereotypeCases.define(self,name='Tagged')
        self.money=Uml.PrimitiveType(name='Money');self.profile.packagedElement.append(self.money)
        self.prop=Uml.Property(name='price',type=self.money,lowerValue=Uml.LiteralInteger(value=0))
        self.stereo.ownedAttribute.append(self.prop)
        apply_profile(self.model,self.profile)

    def tearDown(self):self.session.__exit__(None,None,None)

    @verifies('Stereotype')
    def test_type_identity_unknown_semantics_and_immutable_lexical_edits(self):
        value=PrimitiveValue(self.money,'0012.30')
        app=apply_stereotype(self.model.packagedElement[0],self.stereo,values={'price':value})
        self.assertIs(app.get_value('price'),value)
        self.assertIn(('unsupported stereotype application','Profile.tag:price'),app.validate())
        with self.assertRaises(NativeNotImplemented):value.to_python()
        with self.assertRaises(NativeNotImplemented):app.set_value('price','12.30')
        other=Uml.PrimitiveType(name='Money');self.profile.packagedElement.append(other)
        with self.assertRaises(TypeError):app.set_value('price',PrimitiveValue(other,'12.30'))
        app.set_value('price',value.with_lexical('17.50'))
        self.assertEqual(value.lexical,'0012.30')

    @verifies('Stereotype')
    def test_collection_uniqueness_order_bounds_and_roundtrip_of_whitespace_values(self):
        self.prop.upperValue=Uml.LiteralUnlimitedNatural(value=3);self.prop.isOrdered=True
        a,b=PrimitiveValue(self.money,'a b'),PrimitiveValue(self.money,'')
        app=apply_stereotype(self.model.packagedElement[0],self.stereo,values={'price':[a,a,b]})
        self.assertEqual(app.get_value('price'),(a,b))
        doc=loads(dumps(self.model));restored=next(v for v in doc.runtime_values if hasattr(v,'element'))
        self.assertEqual([v.lexical for v in restored.get_value('price')],['a b',''])
        self.assertIs(restored.get_value('price')[0].classifier,restored._property('price').type)

    @verifies('Stereotype')
    def test_explicit_codec_validates_conversion_and_is_not_serialized(self):
        register_primitive_codec(self.money,decode=Decimal,encode=lambda v:format(v,'f'),validate=lambda v:isinstance(v,Decimal) and v>=0)
        value=PrimitiveValue.from_python(self.money,Decimal('12.30'))
        self.assertEqual(value.to_python(),Decimal('12.30'))
        with self.assertRaises(ValueError):value.with_lexical('-1')
        with self.assertRaises(ValueError):PrimitiveValue.from_python(self.money,Decimal('-1'))
        app=apply_stereotype(self.model.packagedElement[0],self.stereo,values={'price':value})
        self.assertNotIn(('unsupported stereotype application','Profile.tag:price'),app.validate())
        restored=next(v for v in loads(dumps(self.model)).runtime_values if hasattr(v,'element'))
        self.assertEqual(restored.get_value('price').lexical,'12.30')
        with self.assertRaises(NativeNotImplemented):restored.get_value('price').to_python()
        unregister_primitive_codec(self.money)
        self.assertFalse(value.has_semantics)

    @verifies('Stereotype')
    def test_callback_boolean_encoder_contract_and_public_mutation_guard(self):
        register_primitive_codec(self.money,decode=str,encode=str,validate=lambda v:1)
        with self.assertRaises(TypeError):PrimitiveValue(self.money,'12')
        def mutating(text):
            self.model.name='changed'
            return text
        register_primitive_codec(self.money,decode=mutating,encode=str,validate=lambda v:True)
        with self.assertRaises(ValueError):PrimitiveValue(self.money,'12')
        self.assertEqual(self.model.name,'Model')
        register_primitive_codec(self.money,decode=str,encode=lambda v:12,validate=lambda v:True)
        with self.assertRaises(TypeError):PrimitiveValue.from_python(self.money,'12')

    @verifies('Stereotype')
    def test_deleting_definition_clears_values_and_codecs(self):
        register_primitive_codec(self.money,decode=str,encode=str,validate=lambda v:True)
        value=PrimitiveValue(self.money,'12')
        app=apply_stereotype(self.model.packagedElement[0],self.stereo,values={'price':value})
        self.money.delete()
        self.assertEqual(app._values[self.prop],())
        with self.assertRaises(DeletedElementError):value.to_python()
        from umltools.primitive_values import _codecs
        self.assertNotIn(self.money,_codecs)

    @verifies('Stereotype')
    def test_explicitly_typed_literal_default_and_registered_constraint(self):
        self.prop.defaultValue=Uml.LiteralString(type=self.money,value='0012')
        app=apply_stereotype(self.model.packagedElement[0],self.stereo)
        self.assertEqual(app.get_value('price').lexical,'0012')
        rule=Uml.Constraint(name='lexical');self.stereo.ownedRule.append(rule)
        register_profile_constraint(rule,lambda a:a.get_value('price').lexical=='0012')
        self.assertFalse(any(identifier.endswith('::lexical') for _,identifier in app.validate()))

    def test_source_version_candidates_and_export_guard(self):
        def source(namespace):return f'<u:Model xmlns:u="{namespace}" xmlns:x="{XMI_NS}" x:id="m"/>'
        for namespace,expected in [(UML_NS,('2.5.1',)),('http://www.omg.org/spec/UML/20131001',('2.5','2.5.1')),
                                   ('http://www.eclipse.org/uml2/5.0.0/UML',())]:
            doc=loads(source(namespace))
            self.assertEqual(doc.semantic_version,'2.5.1')
            self.assertEqual(doc.source_dialects[doc.uri][0].possible_versions,expected)
            with self.assertRaises(XmiUnsupportedError):dumps(doc,target_version='2.4.1')
            self.assertIn(UML_NS,dumps(doc,target_version='2.5.1'))
        with self.assertRaises(XmiUnsupportedError):loads(source('http://www.omg.org/spec/UML/20110701'))
        legacy=loads(source('http://www.omg.org/spec/UML/20110701'),semantic_version='auto')
        self.assertEqual(legacy.semantic_version,'2.4.1')
