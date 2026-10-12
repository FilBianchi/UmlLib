"""Typed profile runtime values, strict views and explicit user constraints."""
import unittest
import Uml
from umltools import ModelSession, DeletedElementError, DeletionRestrictedError
from umltools.native import NativeNotImplemented
from umltools.stereotypes import apply_profile, apply_stereotype, applications, unapply_profile
from umltools.profile_values import ProfileObject, EnumValue, register_profile_constraint, unregister_profile_constraint
from umltools.profile_filtering import is_metaclass_available, is_element_available, create_profiled_element
from semantic_cases import verifies


def bounded(type_, name, lower=0, upper=1, **kwargs):
    return Uml.Property(name=name, type=type_, lowerValue=Uml.LiteralInteger(value=lower),
                        upperValue=Uml.LiteralUnlimitedNatural(value=upper), **kwargs)


class ProfileValueCases(unittest.TestCase):
    def setUp(self):
        from test_stereotype_applications import StereotypeCases
        self.session = ModelSession(); self.session.__enter__()
        self.profile, self.metamodel, self.model = Uml.Profile(name='Domain'), Uml.Model(name='UML'), Uml.Model(name='M')
        self.element = Uml.Class(name='C'); self.model.packagedElement.append(self.element)
        self.stereo, self.bases = StereotypeCases.define(self, name='DomainClass')
        apply_profile(self.model, self.profile)
        self.string, self.integer = Uml.PrimitiveType(name='String'), Uml.PrimitiveType(name='Integer')
        self.profile.packagedElement.extend([self.string, self.integer])

    def tearDown(self): self.session.__exit__(None, None, None)

    def tag(self, name, type_=None, **kwargs):
        prop = bounded(type_ or self.string, name, **kwargs)
        self.stereo.ownedAttribute.append(prop)
        return prop

    @verifies('Stereotype')
    def test_scalar_defaults_types_required_values_and_atomic_bulk_update(self):
        text = self.tag('label', defaultValue=Uml.LiteralString(value='default'))
        count = self.tag('count', self.integer, lower=1)
        app = apply_stereotype(self.element, self.stereo)
        self.assertEqual(app.get_value('label'), 'default')
        self.assertIn(('stereotype application','Profile.tag:count'), app.validate())
        app.set_values({'label':'set','count':3})
        self.assertEqual(dict(app.tagged_values), {'label':'set','count':3})
        with self.assertRaises(TypeError): app.set_values({'label':'changed','count':True})
        self.assertEqual(app.get_value(text), 'set')
        self.assertEqual(app.get_value(count), 3)
        with self.assertRaises(ValueError): app.set_value(count, None)
        app.unset_value(text)
        self.assertEqual(app.get_value(text), 'default')
        with self.assertRaises(ValueError): app.unset_value(count)
        with self.assertRaises(ValueError): app.set_value(self.bases[0], self.element)
        with self.assertRaises(TypeError): app.tagged_values['label'] = 'bypass'

    @verifies('Stereotype')
    def test_collections_order_uniqueness_bags_and_upper_bounds(self):
        prop = self.tag('labels', upper=2, isOrdered=True)
        bag = self.tag('bag', upper=float('inf'), isUnique=False)
        app = apply_stereotype(self.element, self.stereo, values={'labels':['a','a','b'], 'bag':['x','x']})
        self.assertEqual(app.get_value(prop), ('a','b'))
        self.assertEqual(app.get_value(bag), ('x','x'))
        with self.assertRaises(ValueError): app.set_value(prop, ['a','b','c'])
        with self.assertRaises(TypeError): app.set_value(prop, ['a',None])
        self.assertEqual(app.get_value(prop), ('a','b'))

    @verifies('Stereotype')
    def test_enumeration_and_metaclass_references(self):
        enum = Uml.Enumeration(name='Mode', ownedLiteral=[Uml.EnumerationLiteral(name='fast'),Uml.EnumerationLiteral(name='slow')])
        self.profile.packagedElement.append(enum)
        choice = self.tag('mode', enum)
        ref = self.tag('related', self.bases[0].type)
        app = apply_stereotype(self.element, self.stereo, values={'mode':'fast', 'related':self.element})
        self.assertIsInstance(app.get_value(choice), EnumValue)
        self.assertIs(app.get_value(choice).literal, enum.ownedLiteral[0])
        self.assertIs(app.get_value(ref), self.element)
        with self.assertRaises(TypeError): app.set_value(ref, Uml.Package())
        with self.assertRaises(ValueError): app.set_value(choice, 'missing')
        with self.assertRaises(TypeError): app.set_value(choice, Uml.EnumerationLiteral(name='fast'))
        enum.ownedLiteral[0].delete()
        self.assertIsNone(app.get_value(choice))

    @verifies('Stereotype')
    def test_readonly_initial_values_inherited_tags_and_redefinitions(self):
        inherited = self.tag('code', self.integer, isReadOnly=True, defaultValue=Uml.LiteralInteger(value=1))
        child = Uml.Stereotype(name='Child', generalization=[Uml.Generalization(general=self.stereo)])
        self.profile.packagedElement.append(child)
        refined = bounded(self.integer, 'code', isReadOnly=True, redefinedProperty=[inherited])
        child.ownedAttribute.append(refined)
        app = apply_stereotype(self.element, child, values={'code':2})
        self.assertEqual(app.get_value(refined), 2)
        with self.assertRaises(ValueError): app.get_value(inherited)
        with self.assertRaises(ValueError): app.set_value(refined,3)
        with self.assertRaises(ValueError): app.unset_value(refined)

    @verifies('Stereotype')
    def test_profile_objects_are_not_instance_specifications_and_datatypes_are_immutable(self):
        data = Uml.DataType(name='Payload', ownedAttribute=[bounded(self.integer,'size',lower=1)])
        self.profile.packagedElement.append(data)
        prop = self.tag('payload', data)
        value = ProfileObject(data, self.model, values={'size':4})
        app = apply_stereotype(self.element, self.stereo, values={'payload':value})
        self.assertIs(app.get_value(prop), value)
        self.assertEqual(value.get_value('size'), 4)
        with self.assertRaises(ValueError): value.set_value('size',5)
        with self.assertRaises(TypeError): app.set_value(prop, Uml.InstanceSpecification(classifier=[data]))

    @verifies('Stereotype')
    def test_composite_ownership_cycles_failure_rollback_and_profile_removal(self):
        node = Uml.Class(name='Payload')
        self.profile.packagedElement.append(node)
        children = bounded(node,'children',upper=float('inf'),aggregation=Uml.AggregationKind.composite)
        node.ownedAttribute.append(children)
        prop = self.tag('payload', node, aggregation=Uml.AggregationKind.composite)
        parent, child = ProfileObject(node,self.model), ProfileObject(node,self.model)
        parent.set_value(children,[child])
        with self.assertRaises(ValueError): child.set_value(children,[parent])
        app = apply_stereotype(self.element,self.stereo,values={'payload':parent})
        other = Uml.Class(); self.model.packagedElement.append(other)
        with self.assertRaises(ValueError): apply_stereotype(other,self.stereo,values={'payload':parent})
        self.assertEqual(applications(other), ())
        self.assertIs(app.get_value(prop),parent)
        unapply_profile(self.model,self.profile)
        self.assertTrue(app.is_deleted)
        self.assertTrue(parent.is_deleted)
        self.assertTrue(child.is_deleted)
        self.assertFalse(self.element.is_deleted)
        with self.assertRaises(DeletedElementError): app.get_value(prop)

    @verifies('Stereotype')
    def test_runtime_reference_cleanup_after_base_and_schema_deletion(self):
        cls = Uml.Class(name='Payload'); self.profile.packagedElement.append(cls)
        ref = self.tag('peer', self.stereo)
        prop = self.tag('payload', cls, aggregation=Uml.AggregationKind.composite)
        first = apply_stereotype(self.element,self.stereo)
        other = Uml.Class(); self.model.packagedElement.append(other)
        second = apply_stereotype(other,self.stereo)
        first.set_value(ref,second)
        payload = ProfileObject(cls,self.model)
        second.set_value(prop,payload)
        other.delete()
        self.assertTrue(second.is_deleted)
        self.assertTrue(payload.is_deleted)
        self.assertIsNone(first.get_value(ref))
        ref.delete()
        self.assertNotIn(ref, first._values)

    @verifies('Stereotype')
    def test_opaque_defaults_and_derived_properties_are_explicit_obligations(self):
        default = self.tag('formula',self.integer, defaultValue=Uml.OpaqueExpression(body=['x+1'],language=['custom']))
        derived = self.tag('calculated', self.integer, isDerived=True)
        app = apply_stereotype(self.element,self.stereo)
        with self.assertRaises(NativeNotImplemented): app.get_value(default)
        with self.assertRaises(NativeNotImplemented): app.get_value(derived)
        self.assertIn(('unsupported stereotype application','Profile.tag:formula'),app.validate())
        self.assertIn(('unsupported stereotype application','Profile.tag:calculated'),app.validate())

    @verifies('Stereotype')
    def test_user_constraints_callbacks_boolean_contract_and_mutation_guard(self):
        count = self.tag('count',self.integer)
        constraint = Uml.Constraint(name='positive', specification=Uml.OpaqueExpression(body=['self.count>0'],language=['OCL']))
        self.stereo.ownedRule.append(constraint)
        app = apply_stereotype(self.element,self.stereo,values={'count':2})
        identifier = 'Profile.constraint:Domain::DomainClass::positive'
        self.assertIn(('unsupported stereotype application',identifier),app.validate())
        register_profile_constraint(constraint,lambda a:a.get_value(count)>0)
        self.assertNotIn(('unsupported stereotype application',identifier),app.validate())
        app.set_value(count,-1)
        self.assertIn(('stereotype application',identifier),app.validate())
        register_profile_constraint(constraint,lambda a:1)
        self.assertIn(('invalid stereotype application',identifier),app.validate())
        def mutating(a):
            a.element.name='changed'
            return True
        register_profile_constraint(constraint,mutating)
        self.assertIn(('invalid stereotype application',identifier),app.validate())
        self.assertEqual(self.element.name,'C')
        unregister_profile_constraint(constraint)
        constraint.delete()
        self.assertNotIn(('unsupported stereotype application',identifier),app.validate())

    @verifies('ProfileApplication-isStrict')
    def test_strict_view_does_not_delete_existing_elements_and_factory_rejects_hidden_types(self):
        # A stereotype extending Class makes its subtypes visible. Narrow references
        # alone use exact metaclass identities, while extended types use conformance.
        profile = Uml.Profile(name='OnlyState', metaclassReference=[Uml.ElementImport(importedElement=Uml.Class(name='State'))])
        application = apply_profile(self.model,profile,is_strict=True,create_required=False)
        self.assertTrue(is_metaclass_available(self.model,'State'))
        self.assertFalse(is_element_available(self.element))
        self.assertFalse(self.element.is_deleted)
        with self.assertRaises(ValueError): create_profiled_element(self.model,'Class')
        state = create_profiled_element(self.model,'State')
        self.assertIs(state._extent,self.model._extent)
        application.isStrict=False
        self.assertTrue(is_element_available(self.element))

    @verifies('ProfileApplication-isStrict')
    def test_explicit_references_override_metamodel_and_disjoint_strict_filters_roll_back(self):
        profile = Uml.Profile(name='Narrow',metaclassReference=[Uml.ElementImport(importedElement=Uml.Class(name='State'))],
                              metamodelReference=[Uml.PackageImport(importedPackage=self.metamodel)])
        apply_profile(self.model,profile,is_strict=True,create_required=False)
        self.assertFalse(is_metaclass_available(self.model,'Class'))
        disjoint = Uml.Profile(name='Different',metaclassReference=[Uml.ElementImport(importedElement=Uml.Class(name='Package'))])
        before = set(self.session.elements)
        with self.assertRaises(ValueError): apply_profile(self.model,disjoint,is_strict=True,create_required=False)
        self.assertEqual(set(self.session.elements),before)
        self.assertFalse(any(a.appliedProfile is disjoint for a in self.model.profileApplication))

    @verifies('Stereotype')
    def test_public_element_import_exposes_stereotype_but_private_package_import_does_not(self):
        other_profile = Uml.Profile(name='Wrapper')
        other_model = Uml.Model(profileApplication=[Uml.ProfileApplication(appliedProfile=other_profile)])
        other_element=Uml.Class(); other_model.packagedElement.append(other_element)
        import_ = Uml.PackageImport(importedPackage=self.profile,visibility=Uml.VisibilityKind.private)
        other_profile.packageImport.append(import_)
        with self.assertRaises(ValueError): apply_stereotype(other_element,self.stereo)
        other_profile.packageImport.clear()
        other_profile.elementImport.append(Uml.ElementImport(importedElement=self.stereo))
        app = apply_stereotype(other_element,self.stereo)
        self.assertIs(app.element,other_element)

    @verifies('Stereotype')
    def test_binary_associations_keep_both_navigable_ends_and_rollback_overflow(self):
        left, right = Uml.Class(name='Left'), Uml.Class(name='Right')
        self.profile.packagedElement.extend([left,right])
        targets = bounded(right,'targets',upper=float('inf'))
        owner = bounded(left,'owner')
        left.ownedAttribute.append(targets); right.ownedAttribute.append(owner)
        association = Uml.Association(memberEnd=[targets,owner])
        self.profile.packagedElement.append(association)
        a,b,c = ProfileObject(left,self.model),ProfileObject(right,self.model),ProfileObject(left,self.model)
        a.set_value(targets,[b])
        self.assertIs(b.get_value(owner),a)
        with self.assertRaises(ValueError): c.set_value(targets,[b])
        self.assertEqual(c.get_value(targets),())
        self.assertIs(b.get_value(owner),a)
        b.set_value(owner,None)
        self.assertEqual(a.get_value(targets),())
        c.set_value(targets,[b]); c.delete()
        self.assertIsNone(b.get_value(owner))

    @verifies('Stereotype')
    def test_boolean_real_unlimited_natural_and_custom_primitive(self):
        types = [Uml.PrimitiveType(name=n) for n in ('Boolean','Real','UnlimitedNatural','Money')]
        self.profile.packagedElement.extend(types)
        for type_ in types: self.tag(type_.name,type_)
        app=apply_stereotype(self.element,self.stereo,values={'Boolean':False,'Real':2.5,'UnlimitedNatural':float('inf')})
        self.assertIs(app.get_value('Boolean'),False)
        for key,value in [('Boolean',0),('Real',True),('UnlimitedNatural',-1)]:
            with self.assertRaises((ValueError,TypeError)): app.set_value(key,value)
        with self.assertRaises(NativeNotImplemented): app.set_value('Money',12)

    @verifies('Stereotype')
    def test_rebind_preserves_values_and_failed_rebind_keeps_original_base(self):
        prop=self.tag('label')
        app=apply_stereotype(self.element,self.stereo,values={'label':'preserved'})
        other=Uml.Class(); self.model.packagedElement.append(other)
        app.rebind(other)
        self.assertEqual(app.get_value(prop),'preserved')
        self.assertEqual(applications(self.element),())
        with self.assertRaises(ValueError): app.rebind(Uml.Class())
        self.assertIs(app.element,other)

    @verifies('Stereotype')
    def test_removing_one_importing_profile_preserves_shared_type_until_last_removed(self):
        wrapper=Uml.Profile(name='Wrapper',packageImport=[Uml.PackageImport(importedPackage=self.profile)])
        apply_profile(self.model,wrapper)
        cls=Uml.Class(name='Payload'); self.profile.packagedElement.append(cls)
        obj=ProfileObject(cls,self.model)
        app=apply_stereotype(self.element,self.stereo)
        unapply_profile(self.model,self.profile)
        self.assertFalse(obj.is_deleted); self.assertFalse(app.is_deleted)
        unapply_profile(self.model,wrapper)
        self.assertTrue(obj.is_deleted); self.assertTrue(app.is_deleted)

    @verifies('ProfileApplication-isStrict')
    def test_invalid_strict_argument_leaves_no_application_or_extent_leak(self):
        profile=Uml.Profile()
        before=set(self.session.elements)
        with self.assertRaises(TypeError): apply_profile(self.model,profile,is_strict=1)
        self.assertEqual(set(self.session.elements),before)

    @verifies('ProfileApplication-isStrict')
    def test_metamodel_and_imported_stereotype_references_and_extended_subtypes(self):
        from umltools.profile_filtering import referenced_metaclasses
        wrapper=Uml.Profile(elementImport=[Uml.ElementImport(importedElement=self.stereo)])
        self.assertIn(self.bases[0].type,referenced_metaclasses(wrapper))
        apply_profile(self.model,wrapper,is_strict=True)
        self.assertTrue(is_metaclass_available(self.model,'Component'))
        application=next(a for a in self.model.profileApplication if a.appliedProfile is wrapper)
        application.isStrict=False
        metamodel=Uml.Model(packagedElement=[Uml.Package(packagedElement=[Uml.Class(name='State')])])
        only=Uml.Profile(metamodelReference=[Uml.PackageImport(importedPackage=metamodel)])
        apply_profile(self.model,only,is_strict=True,create_required=False)
        self.assertTrue(is_metaclass_available(self.model,'State'))
        self.assertFalse(is_metaclass_available(self.model,'Class'))

    @verifies('Stereotype')
    def test_schema_deletion_invalidates_runtime_values_without_losing_model(self):
        cls=Uml.Class(name='Payload'); self.profile.packagedElement.append(cls)
        obj=ProfileObject(cls,self.model)
        app=apply_stereotype(self.element,self.stereo)
        self.profile.delete()
        self.assertTrue(obj.is_deleted); self.assertTrue(app.is_deleted)
        self.assertFalse(self.element.is_deleted)

    @verifies('Stereotype')
    def test_callbacks_cannot_create_delete_or_modify_runtime_values(self):
        prop=self.tag('label')
        constraint=Uml.Constraint(name='pure')
        self.stereo.ownedRule.append(constraint)
        app=apply_stereotype(self.element,self.stereo,values={'label':'original'})
        for callback in [lambda a:Uml.Class(),lambda a:a.delete(),lambda a:a.set_value(prop,'changed'),lambda a:a.element.delete()]:
            register_profile_constraint(constraint,callback)
            self.assertTrue(any(category=='invalid stereotype application' for category,_ in app.validate()))
            self.assertFalse(app.is_deleted); self.assertFalse(self.element.is_deleted)
            self.assertEqual(app.get_value(prop),'original')

    @verifies('Stereotype')
    def test_restrict_deletion_accounts_for_runtime_tag_references(self):
        prop=self.tag('related',self.bases[0].type)
        other=Uml.Class(); self.model.packagedElement.append(other)
        app=apply_stereotype(self.element,self.stereo,values={'related':other})
        with self.assertRaises(DeletionRestrictedError): other.delete(on_references='restrict')
        self.assertFalse(other.is_deleted)
        self.assertIs(app.get_value(prop),other)
        other.delete()
        self.assertIsNone(app.get_value(prop))
        app.set_value(prop,self.element)
        self.element.delete(on_references='restrict')
        self.assertTrue(app.is_deleted)

    @verifies('Stereotype')
    def test_package_validation_includes_profile_objects_and_rejects_profile_types_in_model(self):
        cls=Uml.Class(name='Payload',ownedAttribute=[bounded(self.integer,'count',lower=1)])
        self.profile.packagedElement.append(cls)
        value=ProfileObject(cls,self.model)
        self.assertIn(('stereotype application','Profile.tag:count'),self.model.validate())
        value.set_value('count',1)
        self.assertNotIn(('stereotype application','Profile.tag:count'),self.model.validate())
        wrong=Uml.Property(type=cls)
        self.element.ownedAttribute.append(wrong)
        self.assertIn(('stereotype application','Profile.type_in_model'),wrong.validate())
        # The prohibition also applies without an applied Profile.
        unprofiled=Uml.Model(packagedElement=[Uml.Class(ownedAttribute=[Uml.Property(type=cls)])])
        self.assertIn(('stereotype application','Profile.type_in_model'),unprofiled.packagedElement[0].ownedAttribute[0].validate())
