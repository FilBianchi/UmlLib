"""Version-specific graph exchange, independent XML and complete setter sweeps."""
import tempfile
import unittest
from pathlib import Path
from collections import Counter
import xml.etree.ElementTree as ET
import hashlib
import json

import Uml241 as U
import Uml251 as V
from Uml241.xmi import load,loads,dump,dumps,XmiError,XmiReferenceError,XmiUnsupportedError,XMI_NS,UML_NS
from umltools import xmi as generic
from test_uml241_structural import concrete


def xml(body, *, uml=UML_NS,xmi=XMI_NS,extra=''):
    return f'<x:XMI xmlns:x="{xmi}" xmlns:u="{uml}" {extra}>{body}</x:XMI>'


class Xmi241Cases(unittest.TestCase):
    def setUp(self):
        self.session=U.ModelSession();self.session.__enter__()
        self.addCleanup(self.session.__exit__,None,None,None)

    def test_native_forward_references_opposites_identity_and_enums(self):
        source=xml('''<u:Model x:id="m" name="Legacy"><packagedElement x:type="u:Class" x:id="a">
          <ownedAttribute x:type="u:Property" x:id="p" type="b" association="r" aggregation="none"/>
          </packagedElement><packagedElement x:type="u:Association" x:id="r" memberEnd="p q">
          <ownedEnd x:type="u:Property" x:id="q" type="a"/></packagedElement>
          <packagedElement x:type="u:Class" x:id="b"/></u:Model>''')
        doc=loads(source)
        a,b,p,r=map(doc.resolve,['a','b','p','r'])
        self.assertIsInstance(a,U.Class);self.assertNotIsInstance(a,V.Class)
        self.assertIs(p.type,b);self.assertIs(p.owner,a);self.assertIs(p.association,r)
        self.assertIs(p.aggregation,U.AggregationKind.none)
        self.assertEqual(set(r.memberEnd),{p,r.ownedEnd[0]})
        self.assertTrue(doc.complete);self.assertEqual(doc.semantic_version,'2.4.1')
        self.assertIsNot(a._extent,self.session)
        restored=loads(dumps(doc));self.assertIs(restored.resolve('p').type,restored.resolve('b'))

    def test_state_specific_redefinition_and_declared_transition_guard(self):
        original,new=U.State(name='Base'),U.State(name='Derived')
        new.redefinedState=original
        region=U.Region(subvertex=[original,new],transition=[U.Transition(source=original,target=new,guard=U.Constraint(specification=U.LiteralBoolean(value=True)))])
        machine=U.StateMachines.StateMachine(region=[region])
        result=loads(dumps(machine)).roots[0]
        self.assertIs(result.region[0].subvertex[1].redefinedState,result.region[0].subvertex[0])
        edge=result.region[0].transition[0]
        self.assertIs(edge.source,result.region[0].subvertex[0]);self.assertTrue(edge.guard.specification.value)
        self.assertFalse(hasattr(result.region[0].subvertex[0],'redefinedVertex'))

    def test_old_structured_node_derived_composite_witness_roundtrip(self):
        activity=U.Activity();node=U.StructuredActivityNode(name='Nested');node.activity=activity
        result=loads(dumps(activity)).roots[0]
        self.assertEqual(len(result.structuredNode),1)
        self.assertEqual(list(result.node),list(result.group))
        self.assertIs(result.structuredNode[0].activity,result)
        self.assertIs(result.structuredNode[0].owner,result)

    def test_old_loop_variable_stays_noncomposite(self):
        pin=U.OutputPin();loop=U.LoopNode(loopVariable=[pin])
        doc=loads(dumps(loop));restored=next(o for o in doc.roots if isinstance(o,U.LoopNode))
        restored_pin=restored.loopVariable[0]
        self.assertIsNone(restored_pin.owner)
        restored.delete();self.assertFalse(restored_pin.is_deleted)

    def test_model_defined_primitive_types_and_text_values(self):
        money=U.PrimitiveType(name='Money');legacy=U.PrimitiveType(name='EString')
        value=U.LiteralString(type=money,value='0012.30')
        model=U.Model(packagedElement=[money,legacy,U.Class(ownedAttribute=[U.Property(type=money,defaultValue=value),U.Property(type=legacy)])])
        result=loads(dumps(model)).roots[0]
        self.assertEqual(result.packagedElement[0].name,'Money')
        attributes=result.packagedElement[2].ownedAttribute
        self.assertIs(attributes[0].defaultValue.type,attributes[0].type)
        self.assertEqual(attributes[0].defaultValue.value,'0012.30')
        self.assertEqual(attributes[1].type.name,'EString')
        for text in ('INF','-INF','NaN'):
            with self.assertRaises(XmiError):loads(xml(f'<u:LiteralReal value="{text}"/>'))

    def test_pinned_omg_primitive_library_and_mof_annotations(self):
        path=Path(__file__).parent/'fixtures/xmi241/PrimitiveTypes.xmi'
        manifest=json.loads(path.with_name('manifest.json').read_text())
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),manifest['sha256'])
        doc=load(path,strict=False)
        self.assertEqual(len(doc.session.elements),11)
        self.assertEqual({o.name for o in doc.roots[0].packagedElement},{'Boolean','Integer','Real','String','UnlimitedNatural'})
        self.assertFalse(doc.complete)
        data=dumps(doc);again=loads(data,strict=False)
        self.assertEqual({o._xmi_id:(o.__spec__.name,getattr(o,'name',None)) for o in doc.session.elements},
                         {o._xmi_id:(o.__spec__.name,getattr(o,'name',None)) for o in again.session.elements})
        tags=ET.fromstring(dumps(again)).findall('{http://www.omg.org/spec/MOF/20100901}Tag')
        self.assertEqual(len(tags),4)
        self.assertEqual({node.get('element') for node in tags},{'_0','Boolean','Integer','Real'})
        self.assertTrue(any('http://www.omg.org/spec/MOF/20100901' in d.message for d in doc.diagnostics))

    def test_profile_definitions_remain_structural_without_applying_runtime_tags(self):
        profile=U.Profile(name='Domain',URI='urn:domain',packagedElement=[U.Stereotype(name='Tagged')])
        model=U.Model(profileApplication=[U.ProfileApplication(appliedProfile=profile)])
        doc=loads(dumps(model));restored=next(root for root in doc.roots if isinstance(root,U.Model))
        self.assertIsInstance(restored.profileApplication[0].appliedProfile,U.Profile)
        self.assertEqual(restored.profileApplication[0].appliedProfile.URI,'urn:domain')
        self.assertTrue(doc.complete);self.assertEqual(doc.runtime_values,[])

    def test_namespace_detection_ambiguity_and_transport_version(self):
        self.assertEqual(generic.detect_version(xml('<u:Model/>')),'2.4.1')
        doc=generic.loads(xml('<u:Model/>'),semantic_version='auto')
        self.assertIsInstance(doc.roots[0],U.Model)
        self.assertEqual(generic.loads(generic.dumps(doc),semantic_version='auto').semantic_version,'2.4.1')
        for namespace in ('http://www.omg.org/spec/UML/20100901','http://www.omg.org/spec/UML/20131001','http://www.eclipse.org/uml2/4.0.0/UML'):
            data=xml('<u:Model/>',uml=namespace)
            with self.assertRaises(XmiUnsupportedError):generic.loads(data,semantic_version='auto')
        data=xml('<u:Model/>',uml='http://www.omg.org/spec/UML/20100901',xmi='http://www.omg.org/spec/XMI/20100901')
        self.assertTrue(loads(data).complete)
        self.assertEqual(generic.detect_version(xml('<u:Model/>').replace('<x:XMI ','<x:XMI x:version="2.5.1" ')),'2.4.1')

    def test_explicit_metadata_resolves_ambiguous_dialects(self):
        data=xml('<x:Extension extender="UmlLib"><lib:metamodel version="2.4.1"/></x:Extension><u:Model/>',uml='http://www.eclipse.org/uml2/4.0.0/UML',extra='xmlns:lib="urn:umllib:xmi:1"')
        doc=generic.loads(data,semantic_version='auto')
        self.assertTrue(doc.complete);self.assertEqual(doc.source_versions[doc.uri],'2.4.1')
        self.assertEqual(doc.source_dialects[doc.uri][0].semantic_version,'2.4.1')
        for version in ('2.5.1','2.4',''):
            conflict=xml(f'<x:Extension extender="UmlLib"><lib:metamodel version="{version}"/></x:Extension><u:Model/>',extra='xmlns:lib="urn:umllib:xmi:1"')
            with self.assertRaises(XmiUnsupportedError):loads(conflict)
            with self.assertRaises(XmiUnsupportedError):generic.loads(conflict,semantic_version='auto')
        spoofed=data.replace('extender="UmlLib"','extender="Vendor"')
        with self.assertRaises(XmiUnsupportedError):generic.detect_version(spoofed)

    def test_no_implicit_migration_even_in_permissive_mode(self):
        from Uml251.xmi import loads as read25,dumps as write25
        for strict in (True,False):
            with self.assertRaises(XmiUnsupportedError):loads(xml('<u:Model/>',uml=generic.UML_NS),strict=strict)
            with self.assertRaises(XmiUnsupportedError):read25(xml('<u:Model/>'),strict=strict)
        with self.assertRaises(XmiUnsupportedError):dumps(U.Model(),target_version='2.5.1')
        with self.assertRaises(XmiUnsupportedError):write25(U.Model())
        with self.assertRaises(XmiError):generic.dumps([U.Model(),V.Model()])
        with self.assertRaises(XmiError):loads(xml('<u:Model/>'),external_objects={'memory:/other#c':V.Class()})

    def test_resource_scoped_ids_cyclic_imports_and_bundling(self):
        first=xml('<u:Package x:id="p" name="A"><packageImport x:type="u:PackageImport"><importedPackage href="b.xmi#p"/></packageImport></u:Package>')
        second=xml('<u:Package x:id="p" name="B"><packageImport x:type="u:PackageImport"><importedPackage href="a.xmi#p"/></packageImport></u:Package>')
        with tempfile.TemporaryDirectory() as folder:
            a,b=Path(folder)/'a.xmi',Path(folder)/'b.xmi';a.write_text(first);b.write_text(second)
            doc=generic.load(a,semantic_version='auto')
            package=doc.resolve('p');other=package.packageImport[0].importedPackage
            self.assertIs(other.packageImport[0].importedPackage,package);self.assertIsNot(other,package)
            restored=loads(dumps(doc));self.assertEqual(len(restored.roots),2)
            target=Path(folder)/'saved.xmi';dump(doc,target)
            self.assertEqual(Counter(o.__spec__.name for o in doc.session.elements),Counter(o.__spec__.name for o in load(target).session.elements))

    def test_mixed_version_dependency_rolls_back_the_entire_import(self):
        source=xml('<u:Property x:id="p" type="other.xmi#c"/>')
        modern=xml('<u:Class x:id="c"/>',uml=generic.UML_NS)
        before=set(U._engine.UmlElement.__instances__)
        with self.assertRaises(XmiUnsupportedError):loads(source,resources={'other.xmi':modern},strict=False)
        self.assertEqual(set(U._engine.UmlElement.__instances__),before)

    def test_failed_import_rolls_back_external_opposites(self):
        external=U.Class();before=set(U._engine.UmlElement.__instances__)
        source=xml('<u:Property x:id="p" class="memory:/external#c" isStatic="invalid"/>')
        with self.assertRaises(XmiError):loads(source,external_objects={'memory:/external#c':external})
        self.assertEqual(list(external.ownedAttribute),[])
        self.assertEqual(set(U._engine.UmlElement.__instances__),before)

    def test_opaque_profile_applications_are_retained_without_execution(self):
        source=xml('<u:Model x:id="m"/><p:Tagged x:id="app" base_Model="m" custom="42"/>',extra='xmlns:p="urn:domain"')
        with self.assertRaises(XmiUnsupportedError):loads(source)
        doc=loads(source,strict=False)
        self.assertFalse(doc.complete);self.assertEqual(doc.runtime_values,[])
        restored=loads(dumps(doc),strict=False)
        self.assertEqual(ET.fromstring(dumps(restored)).find('{urn:domain}Tagged').get('custom'),'42')
        self.assertFalse(restored.complete)
        self.assertTrue(loads(xml('<u:Model/>'),profile_bindings={'urn:domain':U.Profile()}).complete)

    def test_permissive_extensions_and_unknown_old_features_are_retained(self):
        source=xml('<u:State x:id="s" redefinedVertex="other"><x:Extension extender="Vendor"><v:note>before<v:part/> after</v:note></x:Extension></u:State>',extra='xmlns:v="urn:vendor"')
        with self.assertRaises(XmiUnsupportedError):loads(source)
        doc=loads(source,strict=False);data=dumps(doc)
        self.assertIn('redefinedVertex="other"',data)
        note=ET.fromstring(data).find('.//{urn:vendor}note')
        self.assertEqual(note.text,'before');self.assertEqual(note[0].tail,' after')

    def test_safety_limits_in_auto_detection_and_native_reader(self):
        for read in (loads,lambda data,**options:generic.loads(data,semantic_version='auto',**options)):
            for data in ('<!DOCTYPE x>'+xml('<u:Model/>'),('<!DOCTYPE x>'+xml('<u:Model/>')).encode('utf-16')):
                with self.assertRaises(XmiError):read(data)
            for options in ({'max_bytes':1},{'max_elements':1},{'max_depth':1}):
                with self.assertRaises(XmiError):read(xml('<u:Model/>'),**options)
        with self.assertRaises(XmiReferenceError):loads(xml('<u:Property type="https://example.invalid/types#c"/>'))

    def test_all_549_effective_stored_declarations_roundtrip(self):
        primitives={'Boolean':True,'Integer':1,'Real':1.5,'UnlimitedNatural':2,'String':'value <&>\n'}
        registry=U.Class.__registry__;checked=set()
        for spec in U._engine.SPECIFICATIONS.values():
            for prop in spec.properties.values():
                if prop.flags.get('isDerived')=='true':continue
                cls=concrete(spec.name,prop.id)
                if cls is None:continue
                with self.subTest(property=prop.id):
                    obj=cls()
                    if prop.type in primitives:value=primitives[prop.type]
                    elif hasattr(registry[prop.type],'__spec__'):value=concrete(prop.type)()
                    else:value=next(iter(registry[prop.type]))
                    setattr(obj,prop.name,[value] if prop.upper is None or prop.upper>1 else value)
                    original=dumps(obj);restored=loads(original)
                    self.assertTrue(restored.complete)
                    self.assertEqual(original,dumps(restored))
                    checked.add(prop.id)
        self.assertEqual(len(checked),549)


if __name__=='__main__':unittest.main()
