"""Graph exchange tests: independent XML, ownership and profile value round trips."""
import tempfile
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET
import Uml
from umltools import ModelSession, UmlElement
from umltools.xmi import load,loads,dump,dumps,XmiError,XmiReferenceError,XmiUnsupportedError,XMI_NS,UML_NS
from umltools.stereotypes import apply_profile,apply_stereotype,applications
from umltools.profile_values import ProfileObject
from semantic_cases import verifies


def xml(body, namespaces=''):
    return f'<x:XMI xmlns:x="{XMI_NS}" xmlns:u="{UML_NS}" {namespaces}>{body}</x:XMI>'


class XmiCases(unittest.TestCase):
    def setUp(self): self.session=ModelSession(); self.session.__enter__()
    def tearDown(self): self.session.__exit__(None,None,None)

    def test_forward_references_shared_identity_cycles_and_owned_associations(self):
        source=xml('''<u:Model x:id="m" name="M">
          <packagedElement x:type="u:Class" x:id="a" name="A">
            <ownedAttribute x:type="u:Property" x:id="p" name="peer" type="b" association="assoc"/>
          </packagedElement>
          <packagedElement x:type="u:Association" x:id="assoc" memberEnd="p q">
            <ownedEnd x:type="u:Property" x:id="q" type="a"/>
          </packagedElement>
          <packagedElement x:type="u:Class" x:id="b" name="B"/>
        </u:Model>''')
        doc=loads(source)
        a,b,p,association=map(doc.resolve,['a','b','p','assoc'])
        self.assertIs(p.type,b); self.assertIs(p.association,association)
        self.assertIs(p.owner,a); self.assertIs(association.ownedEnd[0].type,a)
        self.assertEqual(set(association.memberEnd),{p,association.ownedEnd[0]})
        self.assertIsNot(a._extent,self.session)
        again=loads(dumps(doc))
        self.assertIs(again.resolve('p').type,again.resolve('b'))
        self.assertEqual(dumps(again),dumps(loads(dumps(again))))

    def test_state_machine_transitions_share_vertices_and_reference_submachines(self):
        start,state=Uml.Pseudostate(),Uml.State(name='Ready')
        region=Uml.Region(subvertex=[start,state],transition=[Uml.Transition(source=start,target=state)])
        machine=Uml.StateMachines.StateMachine(region=[region])
        other=Uml.StateMachines.StateMachine(region=[Uml.Region(subvertex=[Uml.State(submachine=machine)])])
        doc=loads(dumps([machine,other]))
        first=next(m for m in doc.roots if m.region[0].transition)
        edge=first.region[0].transition[0]
        self.assertIs(edge.source,first.region[0].subvertex[0])
        self.assertIs(edge.target,first.region[0].subvertex[1])
        self.assertTrue(any(s.submachine is first for m in doc.roots for r in m.region for s in r.subvertex if isinstance(s,Uml.State)))

    def test_subset_and_redefined_composite_ends_are_not_duplicated(self):
        node=Uml.StructuredActivityNode(name='Nested')
        activity=Uml.Activity(structuredNode=[node])
        result=loads(dumps(activity)).roots[0]
        self.assertEqual(len(result.structuredNode),1)
        self.assertIs(result.structuredNode[0].activity,result)
        self.assertIs(result.structuredNode[0].inActivity,result)
        self.assertEqual(list(result.node),list(result.structuredNode))

    def test_primitive_enum_string_order_and_explicit_null_defaults(self):
        expression=Uml.OpaqueExpression(body=['a b\n<c> & d','', 'a b\n<c> & d'],language=['custom',''])
        cls=Uml.Class(isActive=None,ownedRule=[Uml.Constraint(specification=expression)])
        result=loads(dumps(cls)).roots[0]
        self.assertIsNone(result.isActive)
        self.assertEqual(list(result.ownedRule[0].specification.body),list(expression.body))
        self.assertEqual(list(result.ownedRule[0].specification.language),list(expression.language))
        literal=loads(dumps(Uml.LiteralUnlimitedNatural(value=float('inf')))).roots[0]
        self.assertEqual(literal.value,float('inf'))
        self.assertIs(loads(dumps(Uml.Pseudostate(kind=Uml.PseudostateKind.fork))).roots[0].kind,Uml.PseudostateKind.fork)

    def test_resource_scoped_ids_relative_paths_and_cyclic_imports(self):
        first=xml('<u:Model x:id="m" name="First"><packagedElement x:type="u:Package" x:id="p"><packageImport x:type="u:PackageImport" x:id="i"><importedPackage href="second.xmi#p"/></packageImport></packagedElement></u:Model>')
        second=xml('<u:Model x:id="m" name="Second"><packagedElement x:type="u:Package" x:id="p"><packageImport x:type="u:PackageImport" x:id="i"><importedPackage href="first.xmi#p"/></packageImport></packagedElement></u:Model>')
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'first.xmi'; path.write_text(first)
            (Path(folder)/'second.xmi').write_text(second)
            doc=load(path)
            p=doc.resolve('p'); other=p.packageImport[0].importedPackage
            self.assertIs(other.packageImport[0].importedPackage,p)
            self.assertIsNot(other,p)
            merged=loads(dumps(doc))
            self.assertEqual(len(merged.roots),2)
            self.assertEqual(len(set(merged.ids)),len(doc.ids))

    def test_explicit_resource_map_and_external_object_references(self):
        external=Uml.Class(name='Existing')
        source=xml('<u:Dependency x:id="d" client="https://example.invalid/types.xmi#c"/>')
        doc=loads(source,external_objects={'https://example.invalid/types.xmi#c':external})
        self.assertIs(doc.roots[0].client[0],external)
        self.assertIs(doc.resolve('https://example.invalid/types.xmi#c'),external)
        data=dumps(doc,bundle=False,external_references={external:'https://example.invalid/types.xmi#c'})
        again=loads(data,external_objects={'https://example.invalid/types.xmi#c':external})
        self.assertIs(again.roots[0].client[0],external)

    def test_missing_reference_duplicate_ids_and_conflicting_explicit_ends_fail(self):
        for source in [xml('<u:Property x:id="p" type="missing"/>'),
                       xml('<u:Class x:id="same"/><u:Class x:id="same"/>'),
                       xml('<u:Model x:id="m"><packagedElement x:type="u:Class" x:id="c" owner="other"/></u:Model><u:Model x:id="other"/>')]:
            with self.assertRaises(XmiError): loads(source)

    def test_failed_import_rolls_back_external_opposites_and_new_instances(self):
        external=Uml.Class(name='Existing')
        before=set(UmlElement.__instances__)
        source=xml('<u:Property x:id="p" class="https://example.invalid/types#c" isStatic="notBoolean"/>')
        with self.assertRaises(XmiError): loads(source,external_objects={'https://example.invalid/types#c':external})
        self.assertEqual(list(external.ownedAttribute),[])
        self.assertEqual(set(UmlElement.__instances__),before)
        self.assertEqual(external.name,'Existing')

    def test_dtd_entities_and_byte_element_depth_limits(self):
        literal=loads(xml('<u:OpaqueExpression><body><![CDATA[<!DOCTYPE ordinary text>]]></body></u:OpaqueExpression>'))
        self.assertEqual(list(literal.roots[0].body),['<!DOCTYPE ordinary text>'])
        for source in ['<!DOCTYPE x [<!ENTITY e "value">]>'+xml('<u:Model/>'),
                       ('<!DOCTYPE x>'+xml('<u:Model/>')).encode('utf-16')]:
            with self.assertRaises(XmiError): loads(source)
        for options in [{'max_bytes':10},{'max_elements':1},{'max_depth':1}]:
            with self.assertRaises(XmiError): loads(xml('<u:Model/>'),**options)

    def test_namespace_qnames_and_uuid_are_preserved(self):
        source=f'<u:Model xmlns:u="{UML_NS}" xmlns:x="{XMI_NS}" x:id="m" x:uuid="persistent"><packagedElement xmlns:z="{UML_NS}" x:type="z:Class" x:id="c"/></u:Model>'
        data=dumps(loads(source))
        self.assertIn('xmi:uuid="persistent"',data)
        self.assertIsInstance(loads(data).resolve('c'),Uml.Class)

    def test_vendor_extension_is_retained_and_diagnosed_without_losing_mixed_text(self):
        source=xml('<u:Model x:id="m"><x:Extension extender="Vendor"><v:note>before<v:item/> after</v:note></x:Extension></u:Model>','xmlns:v="urn:vendor"')
        doc=loads(source)
        self.assertFalse(doc.complete)
        data=dumps(doc); root=ET.fromstring(data)
        note=root.find('.//{urn:vendor}note')
        self.assertEqual(note.text,'before'); self.assertEqual(note[0].tail,' after')
        self.assertFalse(loads(data).complete)

    def test_unknown_feature_is_rejected_or_retained_in_lenient_document(self):
        source=xml('<u:Class x:id="c" vendorFlag="yes"><unknownFeature>data</unknownFeature></u:Class>')
        with self.assertRaises(XmiUnsupportedError): loads(source)
        doc=loads(source,strict=False)
        self.assertFalse(doc.complete)
        data=dumps(doc)
        self.assertIn('vendorFlag="yes"',data)
        self.assertEqual(ET.fromstring(data).find('.//unknownFeature').text,'data')

    def profile(self):
        from test_stereotype_applications import StereotypeCases
        self.profile=Uml.Profile(name='Domain'); self.metamodel=Uml.Model(name='UML')
        self.model=Uml.Model(name='Model',packagedElement=[Uml.Class(name='C')])
        stereo,bases=StereotypeCases.define(self,name='Tagged')
        string=Uml.PrimitiveType(name='String'); integer=Uml.PrimitiveType(name='Integer')
        payload=Uml.Class(name='Payload',ownedAttribute=[Uml.Property(name='size',type=integer)])
        enum=Uml.Enumeration(name='Mode',ownedLiteral=[Uml.EnumerationLiteral(name='fast')])
        self.profile.packagedElement.extend([string,integer,payload,enum])
        stereo.ownedAttribute.extend([Uml.Property(name='label',type=string,defaultValue=Uml.LiteralString(value='default'),lowerValue=Uml.LiteralInteger(value=0)),
            Uml.Property(name='labels',type=string,upperValue=Uml.LiteralUnlimitedNatural(value=float('inf')),
                         lowerValue=Uml.LiteralInteger(value=0),defaultValue=Uml.LiteralString(value='default')),
            Uml.Property(name='mode',type=enum),Uml.Property(name='payload',type=payload,aggregation=Uml.AggregationKind.composite)])
        apply_profile(self.model,self.profile,is_strict=True)
        value=ProfileObject(payload,self.model,values={'size':3})
        app=apply_stereotype(self.model.packagedElement[0],stereo,values={'label':'written','labels':['a b','c'],'mode':'fast','payload':value})
        return app

    @verifies('Stereotype','ProfileApplication-isStrict')
    def test_profile_definitions_typed_runtime_values_composition_and_strictness_roundtrip(self):
        app=self.profile()
        doc=loads(dumps(self.model))
        model=next(r for r in doc.roots if r.name=='Model')
        restored=applications(model.packagedElement[0])[0]
        self.assertEqual(restored.get_value('label'),'written')
        self.assertEqual(restored.get_value('labels'),('a b','c'))
        self.assertEqual(restored.get_value('mode').name,'fast')
        self.assertEqual(restored.get_value('payload').get_value('size'),3)
        self.assertIs(restored.get_value('payload')._composite_owner[0],restored)
        self.assertTrue(model.profileApplication[0].isStrict)
        self.assertEqual(restored.validate(),[])
        self.assertEqual(dumps(doc),dumps(loads(dumps(doc))))

    @verifies('Stereotype')
    def test_explicit_empty_tags_override_literal_defaults(self):
        app=self.profile(); app.set_values({'label':None,'labels':[]})
        doc=loads(dumps(self.model))
        restored=next(v for v in doc.runtime_values if hasattr(v,'element'))
        self.assertIsNone(restored.get_value('label')); self.assertEqual(restored.get_value('labels'),())

    @verifies('Stereotype')
    def test_user_constraint_text_survives_but_python_callbacks_are_not_serialized(self):
        app=self.profile()
        app.stereotype.ownedRule.append(Uml.Constraint(name='custom',specification=Uml.OpaqueExpression(body=['self.label <> null'],language=['OCL'])))
        restored=next(v for v in loads(dumps(self.model)).runtime_values if hasattr(v,'element'))
        self.assertIn(('unsupported stereotype application','Profile.constraint:Domain::Tagged::custom'),restored.validate())

    def test_file_api_writes_only_after_successful_serialization(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'model.xmi'
            dump(Uml.Model(name='M'),path)
            self.assertEqual(load(path).roots[0].name,'M')
            original=path.read_bytes()
            dangling=Uml.Dependency(client=[Uml.Class()])
            with self.assertRaises(XmiReferenceError): dump(dangling,path,bundle=False)
            self.assertEqual(path.read_bytes(),original)

    def test_pathmap_resources_and_multiple_aliases_share_one_physical_resource(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'types.uml';path.write_text(xml('<u:Class x:id="c" name="Type"/>'))
            source=xml('<u:Dependency x:id="d"><client href="pathmap://LIB/types.uml#c"/><supplier href="https://example.invalid/types#c"/></u:Dependency>')
            doc=loads(source,resources={'pathmap://LIB/types.uml':path,'https://example.invalid/types':path})
            self.assertIs(doc.roots[0].client[0],doc.roots[0].supplier[0])
            self.assertIs(doc.resolve('pathmap://LIB/types.uml#c'),doc.roots[0].client[0])
            self.assertEqual(len(doc.session.elements),2)

    def test_xml_base_relative_href_and_resources_in_memory(self):
        source=xml('<u:Property x:id="p" xml:base="https://example.invalid/library/"><type href="types.xmi#c"/></u:Property>')
        doc=loads(source,resources={'https://example.invalid/library/types.xmi':xml('<u:Class x:id="c"/>')})
        self.assertIs(doc.roots[0].type,doc.resolve('https://example.invalid/library/types.xmi#c'))

    def test_vendor_extension_references_do_not_trigger_resource_loading(self):
        source=xml('<u:Class x:id="c"><x:Extension extender="Vendor"><unknown href="https://example.invalid/unavailable#id"/></x:Extension></u:Class>')
        doc=loads(source)
        self.assertFalse(doc.complete)
        self.assertIn('https://example.invalid/unavailable#id',dumps(doc))

    @verifies('Stereotype')
    def test_inline_composite_profile_value_and_readonly_construction_tag(self):
        app=self.profile()
        app._property('label').isReadOnly=True
        tree=ET.fromstring(dumps(self.model))
        tree.set('xmlns:uml',UML_NS)  # ElementTree does not retain QName-only declarations.
        instance=next(n for n in tree if n.tag.endswith('Tagged'))
        value=next(n for n in tree if n.tag.endswith('Payload'))
        ref=instance.find('payload'); instance.remove(ref)
        value.tag='payload';instance.append(value);tree.remove(value)
        result=loads(ET.tostring(tree))
        restored=next(v for v in result.runtime_values if hasattr(v,'element'))
        self.assertEqual(restored.get_value('payload').get_value('size'),3)
        self.assertEqual(restored.get_value('label'),'written')
        with self.assertRaises(ValueError):restored.set_value('label','changed')

    @verifies('Stereotype')
    def test_failed_runtime_import_restores_external_base_application_registry(self):
        app=self.profile()
        other=Uml.Class();self.model.packagedElement.append(other)
        from umltools.profile_values import _records
        before=set(_records)
        source=xml('<p:Tagged x:id="app" base_Class="https://example.invalid/model#c" unknown="bad"/>','xmlns:p="urn:domain"')
        with self.assertRaises(XmiUnsupportedError):
            loads(source,profile_bindings={'urn:domain':self.profile},external_objects={'https://example.invalid/model#c':other})
        self.assertEqual(applications(other),())
        self.assertEqual(set(_records),before)
        self.assertIs(applications(self.model.packagedElement[0])[0],app)

    def test_exchange_query_memoization_ends_before_later_model_edits(self):
        from umltools.semantics import _exchange_query_cache
        doc=loads(dumps(Uml.Class(name='Child',generalization=[Uml.Generalization(general=Uml.Class(name='Parent'))])))
        child=next(c for c in doc.roots if c.name=='Child')
        self.assertEqual([c.name for c in child.allParents()],['Parent'])
        child.generalization.clear()
        self.assertEqual(child.allParents(),[])
        self.assertIsNone(_exchange_query_cache.get())
        with self.assertRaises(XmiError):loads(xml('<u:LiteralInteger value="1_000"/>'))
        self.assertIsNone(_exchange_query_cache.get())

    @verifies('Stereotype')
    def test_unsupported_custom_primitive_tag_is_retained_in_permissive_mode(self):
        app=self.profile()
        custom=Uml.PrimitiveType(name='Money');self.profile.packagedElement.append(custom)
        app.stereotype.ownedAttribute.append(Uml.Property(name='price',type=custom))
        data=dumps(self.model)
        tree=ET.fromstring(data);tree.set('xmlns:uml',UML_NS)
        node=next(n for n in tree if n.tag.endswith('Tagged'));node.set('price','12.30')
        with self.assertRaises(XmiUnsupportedError):loads(ET.tostring(tree))
        doc=loads(ET.tostring(tree),strict=False)
        self.assertFalse(doc.complete)
        self.assertTrue(any(d.code=='unsupported' and d.feature=='price' for d in doc.diagnostics))
        self.assertIn('price="12.30"',dumps(doc))
