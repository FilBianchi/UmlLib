"""Independent UML 2.4.1 runtime profile graphs and transport scenarios."""
import unittest
from decimal import Decimal
import xml.etree.ElementTree as ET
import Uml241 as U
import Uml251 as V
from Uml241.stereotypes import apply_profile,unapply_profile,apply_stereotype,applications
from Uml241.profile_values import ProfileObject,EnumValue,register_profile_constraint,unregister_profile_constraint
from Uml241.profile_filtering import is_metaclass_available,create_profiled_element
from Uml241.primitive_values import PrimitiveValue,register_primitive_codec
from Uml241.native import NativeNotImplemented
from Uml241.xmi import loads,dumps,XmiError,XmiUnsupportedError,XMI_NS,UML_NS


def bounded(type_,name,lower=0,upper=1,**options):
    return U.Property(name=name,type=type_,lowerValue=U.LiteralInteger(value=lower),upperValue=U.LiteralUnlimitedNatural(value=upper),**options)


class Profile241Cases(unittest.TestCase):
    def setUp(self):
        self.session=U.ModelSession();self.session.__enter__()
        self.addCleanup(self.session.__exit__,None,None,None)
        self.profile=U.Profile(name='Domain',URI='urn:domain:241')
        self.metamodel=U.Model(name='UML');self.element=U.Class(name='Entity')
        self.model=U.Model(name='M',packagedElement=[self.element])
        self.stereo,self.bases=self.define()
        self.string,self.integer=U.PrimitiveType(name='String'),U.PrimitiveType(name='Integer')
        self.profile.packagedElement.extend([self.string,self.integer])
        apply_profile(self.model,self.profile)

    def define(self,names=('Class',),name='Tagged',required=False,profile=None):
        profile=profile or self.profile;stereotype=U.Stereotype(name=name);profile.packagedElement.append(stereotype)
        props=[]
        for meta_name in names:
            metaclass=U.Class(name=meta_name);self.metamodel.packagedElement.append(metaclass)
            profile.metaclassReference.append(U.ElementImport(importedElement=metaclass))
            # Old sources allow default 1 at multiple alternative base roles.
            prop=U.Property(name='base_'+meta_name,type=metaclass)
            end=U.ExtensionEnd(type=stereotype,aggregation=U.AggregationKind.composite,lowerValue=U.LiteralInteger(value=1 if required else 0))
            profile.packagedElement.append(U.Extension(ownedEnd=end,memberEnd=[prop,end]))
            stereotype.ownedAttribute.append(prop);props.append(prop)
        return stereotype,props

    def tag(self,name,type_=None,**options):
        prop=bounded(type_ or self.string,name,**options);self.stereo.ownedAttribute.append(prop);return prop

    def test_apply_defaults_required_tags_and_atomic_edits(self):
        label=self.tag('label',defaultValue=U.LiteralString(value='default'))
        count=self.tag('count',self.integer,lower=1)
        app=apply_stereotype(self.element,self.stereo)
        self.assertEqual(app.get_value(label),'default')
        self.assertIn(('stereotype application','Profile.tag:count'),app.validate())
        app.set_values({'label':'changed','count':3})
        with self.assertRaises(TypeError):app.set_values({'label':'lost','count':True})
        self.assertEqual(app.get_value(label),'changed');self.assertEqual(app.get_value(count),3)
        with self.assertRaises(ValueError):app.unset_value(count)
        app.unset_value(label);self.assertEqual(app.get_value(label),'default')
        self.assertEqual(app.validate(),[])

    def test_old_base_roles_are_runtime_prose_not_new_normative_rules(self):
        stereo,props=self.define(('Class','NamedElement'),name='Alternative')
        self.assertTrue(all(p.lowerBound()==1 for p in props))
        with self.assertRaises(ValueError):apply_stereotype(self.element,stereo)
        app=apply_stereotype(self.element,stereo,base_property=props[0])
        self.assertEqual(list(app.base_slots.values()).count(self.element),1)
        self.assertEqual(app.validate(),[])
        self.assertNotIn('Stereotype.base_property_multiplicity_multiple_extension',U._engine.native.CONSTRAINTS)
        self.assertEqual(len(U._engine.native.CONSTRAINTS),433)
        props[1].upperValue=U.LiteralUnlimitedNatural(value=2)
        self.assertIn(('stereotype application','prose:Stereotype.base_link_upper_bound'),app.validate())

    def test_inheritance_redefinitions_readonly_and_no_duplicate_application(self):
        original=self.tag('code',self.integer,isReadOnly=True)
        child=U.Stereotype(name='Child',generalization=[U.Generalization(general=self.stereo)])
        replacement=bounded(self.integer,'code',isReadOnly=True,redefinedProperty=[original])
        child.ownedAttribute.append(replacement);self.profile.packagedElement.append(child)
        app=apply_stereotype(self.element,child,values={'code':7})
        self.assertEqual(app.get_value(replacement),7)
        with self.assertRaises(ValueError):app.get_value(original)
        with self.assertRaises(ValueError):app.set_value(replacement,8)
        with self.assertRaises(ValueError):apply_stereotype(self.element,self.stereo)
        with self.assertRaises(ValueError):apply_stereotype(self.element,child)
        self.assertEqual(applications(self.element),(app,))

    def test_rebind_preserves_values_and_refuses_wrong_metaclass_atomically(self):
        self.tag('name');app=apply_stereotype(self.element,self.stereo,values={'name':'kept'})
        other=U.Class();self.model.packagedElement.append(other)
        app.rebind(other);self.assertEqual(applications(self.element),())
        with self.assertRaises(ValueError):app.rebind(self.model)
        self.assertIs(app.element,other);self.assertEqual(app.get_value('name'),'kept')
        self.assertEqual(applications(other),(app,))

    def test_required_abstract_extensions_are_created_and_removal_keeps_core(self):
        required,bases=self.define(name='Required',required=True);required.isAbstract=True
        child=U.Stereotype(name='Concrete',generalization=[U.Generalization(general=required)])
        self.profile.packagedElement.append(child)
        missing=('stereotype application','Stereotype.required_extension')
        self.assertIn(missing,self.element.validate())
        apply_profile(self.model,self.profile)
        app=next(a for a in applications(self.element) if a.stereotype is child)
        self.assertNotIn(missing,self.element.validate())
        unapply_profile(self.model,self.profile)
        self.assertTrue(app.is_deleted);self.assertFalse(self.element.is_deleted)
        self.assertEqual(list(self.model.profileApplication),[])

    def test_modeled_slots_have_old_runtime_diagnostics_and_profile_cleanup(self):
        target=U.InstanceSpecification(classifier=[self.bases[0].type]);self.model.packagedElement.append(target)
        value=U.InstanceValue(instance=target)
        slot=U.Slot(definingFeature=self.bases[0],value=[value])
        modeled=U.InstanceSpecification(classifier=[self.stereo],slot=[slot]);self.model.packagedElement.append(modeled)
        self.assertFalse(any(kind=='stereotype application' for kind,rule in modeled.validate()))
        slot.value.append(U.InstanceValue(instance=target))
        self.assertIn(('stereotype application','prose:Stereotype.base_link_upper_bound'),modeled.validate())
        unapply_profile(self.model,self.profile)
        self.assertTrue(modeled.is_deleted);self.assertTrue(slot.is_deleted);self.assertFalse(target.is_deleted)

    def test_dependent_profile_must_be_removed_first(self):
        dependent=U.Profile(name='Dependent',packageImport=[U.PackageImport(importedPackage=self.profile)])
        apply_profile(self.model,dependent)
        app=apply_stereotype(self.element,self.stereo)
        with self.assertRaises(ValueError):unapply_profile(self.model,self.profile)
        self.assertFalse(app.is_deleted);self.assertEqual(len(self.model.profileApplication),2)
        unapply_profile(self.model,dependent);self.assertFalse(app.is_deleted)
        unapply_profile(self.model,self.profile);self.assertTrue(app.is_deleted)

    def test_collections_bags_enums_and_typed_metaclass_references(self):
        labels=self.tag('labels',upper=2,isOrdered=True)
        bag=self.tag('bag',upper=float('inf'),isUnique=False)
        enum=U.Enumeration(name='Mode',ownedLiteral=[U.EnumerationLiteral(name='fast')]);self.profile.packagedElement.append(enum)
        self.tag('mode',enum);self.tag('related',self.bases[0].type)
        app=apply_stereotype(self.element,self.stereo,values={'labels':['a','a','b'],'bag':['x','x'],'mode':'fast','related':self.element})
        self.assertEqual(app.get_value(labels),('a','b'));self.assertEqual(app.get_value(bag),('x','x'))
        self.assertIsInstance(app.get_value('mode'),EnumValue)
        with self.assertRaises(ValueError):app.set_value(labels,['a','b','c'])
        with self.assertRaises(TypeError):app.set_value('related',V.Class())
        enum.ownedLiteral[0].delete();self.assertIsNone(app.get_value('mode'))

    def test_class_composition_datatype_immutability_and_lifecycle(self):
        payload=U.Class(name='Payload',ownedAttribute=[bounded(self.integer,'size')])
        value_type=U.DataType(name='Value',ownedAttribute=[bounded(self.integer,'value')])
        self.profile.packagedElement.extend([payload,value_type])
        self.tag('payload',payload,aggregation=U.AggregationKind.composite)
        self.tag('value',value_type)
        child=ProfileObject(payload,self.model,values={'size':4});value=ProfileObject(value_type,self.model,values={'value':2})
        app=apply_stereotype(self.element,self.stereo,values={'payload':child,'value':value})
        with self.assertRaises(ValueError):value.set_value('value',3)
        peer=U.Class();self.model.packagedElement.append(peer)
        other=apply_stereotype(peer,self.stereo)
        with self.assertRaises(ValueError):other.set_value('payload',child)
        self.assertIs(app.get_value('payload'),child)
        self.element.delete();self.assertTrue(app.is_deleted);self.assertTrue(child.is_deleted)
        self.assertFalse(value.is_deleted)

    def test_binary_profile_associations_keep_inverse_and_atomic_bounds(self):
        first,second=U.Class(name='First'),U.Class(name='Second');self.profile.packagedElement.extend([first,second])
        forward,back=bounded(second,'next'),bounded(first,'previous')
        first.ownedAttribute.append(forward);second.ownedAttribute.append(back)
        self.profile.packagedElement.append(U.Association(memberEnd=[forward,back]))
        a,b,c=ProfileObject(first,self.model),ProfileObject(second,self.model),ProfileObject(first,self.model)
        a.set_value(forward,b);self.assertIs(b.get_value(back),a)
        with self.assertRaises(ValueError):c.set_value(forward,b)
        self.assertIsNone(c.get_value(forward));self.assertIs(b.get_value(back),a)
        b.set_value(back,None);self.assertIsNone(a.get_value(forward))

    def test_association_end_ownership_uses_real_other_end_in_old_metamodel(self):
        from Uml241.native import check
        target=U.Class(name='Payload');self.profile.packagedElement.append(target)
        prop=bounded(target,'payload');self.stereo.ownedAttribute.append(prop)
        other=bounded(self.stereo,'back')
        association=U.Association(memberEnd=[prop,other],ownedEnd=[other]);self.profile.packagedElement.append(association)
        self.assertIsNone(prop.opposite)
        self.assertTrue(check(self.stereo,'Stereotype.associationEndOwnership'))
        association.ownedEnd.remove(other);target.ownedAttribute.append(other)
        self.assertFalse(check(self.stereo,'Stereotype.associationEndOwnership'))

    def test_user_constraint_evidence_and_mutation_guards_are_isolated(self):
        self.tag('count',self.integer)
        constraint=U.Constraint(name='positive',specification=U.OpaqueExpression(body=['count > 0'],language=['OCL']))
        self.stereo.ownedRule.append(constraint)
        app=apply_stereotype(self.element,self.stereo,values={'count':2})
        self.assertTrue(any(category=='unsupported stereotype application' for category,_ in app.validate()))
        register_profile_constraint(constraint,lambda value:value.get_value('count')>0)
        self.assertEqual(app.validate(),[])
        register_profile_constraint(constraint,lambda value:value.set_value('count',3) or True)
        self.assertTrue(any(category=='invalid stereotype application' for category,_ in app.validate()))
        self.assertEqual(app.get_value('count'),2)
        unregister_profile_constraint(constraint)
        from umltools.profile_values import register_profile_constraint as register25
        with self.assertRaises(TypeError):register25(constraint,lambda value:True)

    def test_custom_primitives_keep_type_identity_codec_and_xmi_lexical_value(self):
        money=U.PrimitiveType(name='Money');self.profile.packagedElement.append(money)
        self.tag('price',money)
        register_primitive_codec(money,decode=Decimal,encode=str,validate=lambda value:isinstance(value,Decimal) and value>=0)
        app=apply_stereotype(self.element,self.stereo,values={'price':PrimitiveValue.from_python(money,Decimal('0012.30'))})
        self.assertEqual(app.get_value('price').to_python(),Decimal('12.30'))
        doc=loads(dumps(self.model));value=doc.runtime_values[0].get_value('price')
        self.assertEqual(value.lexical,'12.30');self.assertEqual(value.classifier.name,'Money')
        self.assertFalse(value.has_semantics)
        self.assertTrue(any(category=='unsupported stereotype application' for category,_ in doc.runtime_values[0].validate()))

    def test_unknown_bounds_and_defaults_remain_unsupported(self):
        prop=self.tag('value')
        prop.upperValue=U.OpaqueExpression()
        app=apply_stereotype(self.element,self.stereo)
        with self.assertRaises(NativeNotImplemented):app.get_value(prop)
        with self.assertRaises(NativeNotImplemented):app.set_value(prop,'x')
        self.assertIn(('unsupported stereotype application','Profile.tag:value'),app.validate())
        prop.upperValue=U.LiteralUnlimitedNatural(value=1);prop.defaultValue=U.OpaqueExpression()
        with self.assertRaises(NativeNotImplemented):app.get_value(prop)

    def test_strict_filter_is_a_view_and_conflicts_roll_back(self):
        hidden=U.State();region=U.Region(subvertex=[hidden]);self.model.packagedElement.append(U.StateMachines.StateMachine(region=[region]))
        apply_profile(self.model,self.profile,is_strict=True)
        self.assertTrue(is_metaclass_available(self.model,'Class'));self.assertFalse(is_metaclass_available(self.model,'State'))
        self.assertFalse(hidden.is_deleted)
        with self.assertRaises(ValueError):create_profiled_element(self.model,'State')
        self.assertIsInstance(create_profiled_element(self.model,'Class'),U.Class)
        other=U.Profile(name='Other');self.define(('State',),profile=other)
        with self.assertRaises(ValueError):apply_profile(self.model,other,is_strict=True)
        self.assertEqual(len(self.model.profileApplication),1)

    def test_xmi_typed_tags_shared_references_and_explicit_empty_values(self):
        self.tag('label',defaultValue=U.LiteralString(value='fallback'))
        self.tag('labels',upper=3,defaultValue=U.LiteralString(value='default'),isOrdered=True)
        self.tag('related',self.bases[0].type)
        app=apply_stereotype(self.element,self.stereo,values={'label':None,'labels':[],'related':self.element})
        self.model.profileApplication[0].isStrict=True
        doc=loads(dumps(self.model));restored=next(a for a in doc.runtime_values if hasattr(a,'element'))
        self.assertIs(restored.get_value('related'),restored.element)
        self.assertIsNone(restored.get_value('label'));self.assertEqual(restored.get_value('labels'),())
        self.assertEqual(restored.validate(),[]);self.assertTrue(doc.complete)
        self.assertEqual(dumps(doc),dumps(loads(dumps(doc))))

    def test_independent_xml_application_with_explicit_external_profile_binding(self):
        self.tag('label')
        source=f'<x:XMI xmlns:x="{XMI_NS}" xmlns:u="{UML_NS}" xmlns:d="urn:external"><u:Model x:id="m"><profileApplication x:type="u:ProfileApplication"><appliedProfile href="memory:/profile#p"/></profileApplication><packagedElement x:type="u:Class" x:id="c"/></u:Model><d:Tagged x:id="app" base_Class="c" label="external"/></x:XMI>'
        doc=loads(source,external_objects={'memory:/profile#p':self.profile},profile_bindings={'urn:external':self.profile})
        self.assertTrue(doc.complete);self.assertEqual(doc.runtime_values[0].get_value('label'),'external')
        self.assertIs(doc.runtime_values[0].element,doc.resolve('c'))

    def test_duplicate_xml_application_is_rejected_or_retained_with_diagnostics(self):
        data=dumps(self.model)
        app=apply_stereotype(self.element,self.stereo);tree=ET.fromstring(dumps(self.model));tree.set('xmlns:uml',UML_NS)
        import copy
        duplicate=copy.deepcopy(tree.find('{urn:domain:241}Tagged'));duplicate.set('{'+XMI_NS+'}id','duplicate');tree.append(duplicate)
        with self.assertRaises(XmiError):loads(ET.tostring(tree))
        doc=loads(ET.tostring(tree),strict=False)
        self.assertFalse(doc.complete);self.assertEqual(len(doc.runtime_values),1)
        self.assertTrue(any('cannot be applied twice' in d.message for d in doc.diagnostics))
        self.assertEqual(len(ET.fromstring(dumps(doc)).findall('{urn:domain:241}Tagged')),2)
        with self.assertRaises(XmiError):loads(data,profile_bindings={'urn:foreign':V.Profile()})

    def test_failed_xmi_import_restores_external_application_and_records(self):
        self.tag('count',self.integer);app=apply_stereotype(self.element,self.stereo,values={'count':7})
        temporary,_=self.define(name='Temporary')
        before=set(U._engine.UmlElement.__instances__)
        from importlib import import_module
        values_module=import_module(U._engine.__name__+'.profile_values')
        records=set(values_module._records)
        source=f'<x:XMI xmlns:x="{XMI_NS}" xmlns:u="{UML_NS}" xmlns:d="urn:external"><u:Model x:id="m"><profileApplication><appliedProfile href="memory:/profile#p"/></profileApplication><packagedElement x:type="u:Class" x:id="c"/></u:Model><d:Temporary x:id="first" base_Class="memory:/external#c"/><d:Tagged x:id="second" base_Class="c" count="not_integer"/></x:XMI>'
        with self.assertRaises(XmiError):loads(source,external_objects={'memory:/profile#p':self.profile,'memory:/external#c':self.element},profile_bindings={'urn:external':self.profile})
        self.assertEqual(set(U._engine.UmlElement.__instances__),before)
        self.assertEqual(set(values_module._records),records)
        self.assertEqual(app.get_value('count'),7);self.assertEqual(applications(self.element),(app,))

    def test_backend_and_codec_cross_version_values_are_rejected(self):
        self.tag('related',self.bases[0].type)
        with self.assertRaises(TypeError):apply_profile(self.model,V.Profile())
        with self.assertRaises(TypeError):apply_stereotype(V.Class(),self.stereo)
        from umltools.stereotypes import applications as apps25
        app=apply_stereotype(self.element,self.stereo)
        with self.assertRaises(TypeError):apps25(self.element)
        with self.assertRaises(TypeError):app.set_value('related',V.Class())
        with self.assertRaises(TypeError):register_primitive_codec(V.PrimitiveType(name='Money'),decode=str,encode=str,validate=lambda x:True)

    def test_nested_profiles_with_same_classifier_name_have_distinct_xml_namespaces(self):
        nested=U.Profile(name='Nested',URI='urn:nested:241');self.profile.packagedElement.append(nested)
        other,bases=self.define(profile=nested)
        first=apply_stereotype(self.element,self.stereo)
        second=apply_stereotype(self.element,other)
        doc=loads(dumps(self.model))
        self.assertTrue(doc.complete);self.assertEqual(len(doc.runtime_values),2)
        self.assertEqual({a.stereotype.profile.URI for a in doc.runtime_values},{self.profile.URI,nested.URI})


if __name__=='__main__':unittest.main()
