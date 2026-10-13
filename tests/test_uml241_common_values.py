"""Audited 2.4.1 behavior, including differences from 2.5.1."""
import unittest
import Uml241 as U
import Uml251 as V
from Uml241.native import check,NativeNotImplemented
from Uml241.expression_semantics import register_expression_facts


class CommonValues241Cases(unittest.TestCase):
    def setUp(self):
        self.session=U.ModelSession();self.session.__enter__()
        self.addCleanup(self.session.__exit__,None,None,None)

    def test_qualified_names_and_owned_namespace_queries_follow_mutations(self):
        feature=U.Property(name='id');classifier=U.Class(name='Customer',ownedAttribute=[feature])
        inner=U.Package(name='Domain',packagedElement=[classifier]);root=U.Model(name='Root',packagedElement=[inner])
        self.assertEqual(feature.qualifiedName,'Root::Domain::Customer::id')
        self.assertEqual(feature.allNamespaces(),[classifier,inner,root])
        self.assertEqual(feature.allOwningPackages(),[])
        self.assertEqual(classifier.allOwningPackages(),[inner,root])
        self.assertIs(feature.uml_operation('NamedElement','namespace'),classifier)
        self.assertEqual(inner.uml_operation('Namespace','ownedMember'),[classifier])
        inner.name='Renamed';self.assertIn('::Renamed::',feature.qualifiedName)
        inner.name=None;self.assertIsNone(feature.qualifiedName)
        self.assertTrue(check(feature,'NamedElement.has_no_qualified_name'))

    def test_template_namespace_and_root_visibility_differ_from_251(self):
        def formal(api):
            element=api.Class(name='T')
            parameter=api.ClassifierTemplateParameter(ownedParameteredElement=element)
            generic=api.Class(name='Generic',ownedTemplateSignature=api.RedefinableTemplateSignature(ownedParameter=[parameter]))
            root=api.Model(name='Root',packagedElement=[generic])
            return element,root
        old,old_root=formal(U);new,new_root=formal(V)
        self.assertEqual(old.allNamespaces(),[])
        self.assertEqual(old.qualifiedName,'T')
        self.assertEqual(new.qualifiedName,'Root::Generic::T')
        self.assertFalse(check(old_root,'NamedElement.visibility_needs_ownership'))
        from Uml251.native import check as check25
        self.assertTrue(check25(new_root,'NamedElement.visibility_needs_ownership'))

    def test_import_aliases_collisions_and_local_shadowing(self):
        a,b=U.Class(name='A'),U.Class(name='B')
        namespace=U.Package(elementImport=[U.ElementImport(importedElement=a,alias='Same'),U.ElementImport(importedElement=b,alias='Same')])
        self.assertEqual(namespace.importedMember,[])
        namespace.elementImport[1].alias='Other'
        self.assertEqual(set(namespace.importedMember),{a,b})
        self.assertEqual(namespace.getNamesOfMember(a),['Same'])
        namespace.packagedElement.append(U.Class(name='Same'))
        self.assertEqual(namespace.importedMember,[b])
        self.assertTrue(namespace.membersAreDistinguishable())

    def test_private_imports_are_visible_inside_but_not_reexported(self):
        public=U.Class(name='Public');private=U.Class(name='Private',visibility=U.VisibilityKind.private)
        source=U.Package(packagedElement=[public,private])
        middle=U.Package(packageImport=[U.PackageImport(importedPackage=source,visibility=U.VisibilityKind.private)])
        target=U.Package(packageImport=[U.PackageImport(importedPackage=middle)])
        self.assertEqual(source.visibleMembers(),[public])
        self.assertEqual(middle.importedMember,[public])
        self.assertEqual(middle.visibleMembers(),[])
        self.assertEqual(target.importedMember,[])
        middle.packageImport[0].visibility=U.VisibilityKind.public
        self.assertEqual(target.importedMember,[public])
        with self.assertRaises(ValueError):source.makesVisible(U.Class())

    def test_import_constraints_and_cycle_detection(self):
        item=U.Class(visibility=U.VisibilityKind.private)
        imp=U.ElementImport(importedElement=item)
        self.assertFalse(check(imp,'ElementImport.imported_element_is_public'))
        imp.visibility=U.VisibilityKind.protected
        self.assertFalse(check(imp,'ElementImport.visibility_public_or_private'))
        a,b=U.Package(),U.Package()
        a.packageImport.append(U.PackageImport(importedPackage=b));b.packageImport.append(U.PackageImport(importedPackage=a))
        with self.assertRaises(ValueError):a.visibleMembers()

    def test_parameterable_compatibility_direction_is_version_specific(self):
        class OldSpecific(U.Dependency):pass
        class NewSpecific(V.Dependency):pass
        self.assertTrue(U.Dependency().isCompatibleWith(OldSpecific()))
        self.assertFalse(OldSpecific().isCompatibleWith(U.Dependency()))
        self.assertFalse(V.Dependency().isCompatibleWith(NewSpecific()))

    def test_templates_and_parameter_substitution_rules(self):
        formal=U.Dependency();parameter=U.TemplateParameter(ownedParameteredElement=formal)
        signature=U.TemplateSignature(ownedParameter=[parameter]);owner=U.Package(ownedTemplateSignature=signature)
        self.assertTrue(formal.isTemplateParameter())
        self.assertTrue(owner.uml_operation('TemplateableElement','isTemplate'))
        self.assertIn(formal,owner.parameterableElements())
        binding=U.TemplateBinding(signature=signature,parameterSubstitution=[U.TemplateParameterSubstitution(formal=parameter,actual=U.Dependency())])
        self.assertTrue(check(binding,'TemplateBinding.parameter_substitution_formal'))
        self.assertTrue(check(binding.parameterSubstitution[0],'TemplateParameterSubstitution.must_be_compatible'))
        binding.parameterSubstitution.append(U.TemplateParameterSubstitution(formal=parameter,actual=U.Dependency()))
        self.assertFalse(check(binding,'TemplateBinding.one_parameter_substitution'))

    def test_cardinalities_unlimited_bounds_and_undefined_expressions(self):
        def multiplicity(low,high):return U.Property(lowerValue=U.LiteralInteger(value=low),upperValue=U.LiteralUnlimitedNatural(value=high))
        broad,narrow=multiplicity(0,float('inf')),multiplicity(2,5)
        self.assertTrue(narrow.compatibleWith(broad));self.assertFalse(broad.compatibleWith(narrow))
        self.assertTrue(broad.includesMultiplicity(narrow));self.assertTrue(narrow.includesCardinality(5))
        self.assertFalse(narrow.includesCardinality(6));self.assertTrue(narrow.is_(2,5))
        with self.assertRaises(TypeError):narrow.includesCardinality(True)
        undefined=U.Property(lowerValue=U.OpaqueExpression(),upperValue=U.OpaqueExpression())
        self.assertIsNone(undefined.lowerBound());self.assertIsNone(undefined.upperBound())
        self.assertTrue(check(undefined,'MultiplicityElement.upper_ge_lower'))
        self.assertFalse(undefined.is_(1,1))
        with self.assertRaises(ValueError):undefined.includesCardinality(1)
        undefined.upperValue=U.LiteralUnlimitedNatural(value=3)
        self.assertTrue(undefined.isMultivalued())

    def test_constraint_and_bound_expression_facts_are_explicit(self):
        constraint=U.Constraint(specification=U.LiteralBoolean(value=False))
        self.assertTrue(check(constraint,'Constraint.boolean_value'))
        self.assertTrue(check(constraint,'Constraint.value_specification_boolean'))
        self.assertTrue(check(constraint,'Constraint.no_side_effects'))
        constraint.specification=U.LiteralInteger(value=1)
        self.assertFalse(check(constraint,'Constraint.value_specification_boolean'))
        expression=U.OpaqueExpression(body=['foreign()'],language=['custom'])
        prop=U.Property(lowerValue=expression)
        with self.assertRaises(NativeNotImplemented):check(prop,'MultiplicityElement.value_specification_constant')
        register_expression_facts(expression,constant=True,pure=False)
        self.assertTrue(check(prop,'MultiplicityElement.value_specification_constant'))
        self.assertFalse(check(prop,'MultiplicityElement.value_specification_no_side_effects'))

    def test_opaque_return_only_rule_and_result_selection(self):
        incoming=U.Parameter(direction=U.ParameterDirectionKind.in_);returned=U.Parameter(direction=U.ParameterDirectionKind.return_)
        expression=U.OpaqueExpression(behavior=U.OpaqueBehavior(ownedParameter=[incoming,returned]))
        self.assertFalse(check(expression,'OpaqueExpression.only_return_result_parameters'))
        self.assertTrue(check(expression,'OpaqueExpression.one_return_result_parameter'))
        self.assertIs(expression.result,returned)
        expression.behavior.ownedParameter.remove(incoming)
        self.assertTrue(check(expression,'OpaqueExpression.only_return_result_parameters'))
        expression.behavior.ownedParameter.append(U.Parameter(direction=U.ParameterDirectionKind.return_))
        with self.assertRaises(ValueError):_ = expression.result
        modern=V.OpaqueExpression(behavior=V.OpaqueBehavior(ownedParameter=[V.Parameter(direction=V.ParameterDirectionKind.in_),V.Parameter(direction=V.ParameterDirectionKind.return_)]))
        from Uml251.native import check as check25
        self.assertTrue(check25(modern,'OpaqueExpression.only_in_or_return_parameters'))
        with self.assertRaises(ValueError):expression.isPositive()

    def test_string_expressions_and_temporal_multiplicities(self):
        text=U.StringExpression(operand=[U.LiteralString(value='a'),U.LiteralString(value='b')])
        outer=U.StringExpression(subExpression=[text])
        self.assertEqual(outer.stringValue(),'ab')
        self.assertTrue(check(outer,'StringExpression.subexpressions'))
        text.operand.append(U.LiteralInteger(value=2))
        self.assertFalse(check(text,'StringExpression.operands'))
        with self.assertRaises(ValueError):text.stringValue()
        observation=U.DurationObservation(event=[U.Class(),U.Class()],firstEvent=[True])
        self.assertFalse(check(observation,'DurationObservation.first_event_multiplicity'))
        observation.firstEvent.append(False)
        self.assertTrue(check(observation,'DurationObservation.first_event_multiplicity'))
