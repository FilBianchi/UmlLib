import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from umltools.xmi import XmiDocument, loads, load, dumps, XmiReferenceError


class DocumentCases(unittest.TestCase):
    def versions(self):
        return ('2.4.1','2.5.1')

    def test_create_move_detach_export_scopes_and_roundtrip(self):
        for version in self.versions():
            with self.subTest(version=version):
                doc=XmiDocument.new('M',semantic_version=version)
                model=doc.roots[0]
                a=doc.create('Package',owner=model,feature='packagedElement',name='A')
                b=doc.create('Package',owner=model,feature='packagedElement',name='B')
                cls=doc.create('Class',owner=a,feature='packagedElement',name='C')
                identity=doc.identity(cls)
                doc.move(cls,owner=b,feature='packagedElement')
                self.assertIs(cls.owner,b)
                self.assertEqual(list(a.packagedElement),[])
                self.assertIs(doc.resolve(identity),cls)
                doc.detach(cls)
                self.assertIsNone(cls.owner)
                full=loads(dumps(doc),semantic_version='auto')
                self.assertEqual(len(full.session.elements),4)
                reachable=loads(doc.dumps(scope='reachable',roots=[model]),semantic_version='auto')
                self.assertEqual(len(reachable.session.elements),3)
                with self.assertRaises(ValueError):doc.dumps(scope='reachable')
                self.assertEqual(full.semantic_version,version)

    def test_failed_move_restores_containment_and_cached_collections(self):
        for version in self.versions():
            with self.subTest(version=version):
                doc=XmiDocument.new(semantic_version=version)
                model=doc.roots[0]
                a=doc.create('Package',owner=model,feature='packagedElement')
                b=doc.create('Package',owner=a,feature='packagedElement')
                cached=model.packagedElement
                identities=dict(doc.ids)
                with self.assertRaises(ValueError):doc.move(a,owner=b,feature='packagedElement')
                self.assertIs(a.owner,model)
                self.assertIs(b.owner,a)
                self.assertEqual(list(cached),[a])
                self.assertEqual(doc.ids,identities)
                with self.assertRaises(TypeError):doc.move(a,owner=b,feature='elementImport')
                self.assertIs(a.owner,model)

    def test_direct_mutations_reconciled_and_deleted_id_not_resolved(self):
        for version in self.versions():
            with self.subTest(version=version):
                doc=XmiDocument.new(semantic_version=version)
                model=doc.roots[0]
                cls=doc.create('Class',owner=model,feature='packagedElement')
                identity=doc.identity(cls)
                model.packagedElement=[]
                restored=loads(dumps(doc),semantic_version='auto')
                self.assertEqual(len(restored.session.elements),2)
                cls.delete()
                with self.assertRaises(XmiReferenceError):doc.resolve(identity)
                doc.synchronize()
                self.assertNotIn(identity,doc.ids)
                self.assertEqual(len(loads(doc.dumps(),semantic_version='auto').session.elements),1)

    def test_creation_failure_cross_document_and_version_guards(self):
        for version in self.versions():
            with self.subTest(version=version):
                doc=XmiDocument.new(semantic_version=version)
                model=doc.roots[0]
                count=len(doc.session.elements)
                with self.assertRaises(TypeError):doc.create('Classifier')
                with self.assertRaises(TypeError):doc.create('Class',name=42)
                self.assertEqual(len(doc.session.elements),count)
                other=XmiDocument.new(semantic_version=version)
                with self.assertRaises(ValueError):doc.create('Class',owner=other.roots[0],feature='packagedElement')
                with self.assertRaises(ValueError):doc.set_value(model,'packagedElement',[other.roots[0]])
                self.assertEqual(list(model.packagedElement),[])
                with doc.session:
                    local=doc.create('Class')
                self.assertIn(local,doc.session.elements)

    def test_failed_creation_does_not_delete_existing_composite_arguments(self):
        for version in self.versions():
            with self.subTest(version=version):
                doc=XmiDocument.new(semantic_version=version)
                owner=doc.create('Class')
                identities=dict(doc.ids)
                count=len(doc.session.elements)
                with self.assertRaises(ValueError):
                    doc.create('Class',owner=owner,feature='nestedClassifier',nestedClassifier=[owner])
                self.assertFalse(owner.is_deleted)
                self.assertIsNone(owner.owner)
                self.assertEqual(list(owner.nestedClassifier),[])
                self.assertEqual(len(doc.session.elements),count)
                self.assertEqual(doc.ids,identities)

    def test_public_save_is_atomic_and_preserves_ids(self):
        for version in self.versions():
            with self.subTest(version=version),tempfile.TemporaryDirectory() as folder:
                path=Path(folder)/'m.xmi'
                doc=XmiDocument.new(semantic_version=version)
                cls=doc.create('Class',name='C')
                identity=doc.identity(cls).split('#')[-1]
                doc.save(path)
                original=path.read_bytes()
                restored=load(path,semantic_version='auto')
                self.assertEqual(restored.resolve(identity).name,'C')
                exchange=__import__(type(doc).__module__,fromlist=['*'])
                with patch.object(exchange.os,'replace',side_effect=OSError('locked target')):
                    with self.assertRaises(OSError):doc.save(path)
                self.assertEqual(path.read_bytes(),original)
                self.assertFalse(list(Path(folder).glob('.umllib-*.tmp')))

    def test_located_validation_legacy_compatibility_and_json(self):
        for version in self.versions():
            with self.subTest(version=version):
                doc=XmiDocument.new(semantic_version=version)
                g=doc.create('Generalization')
                before=g.validate()
                report=doc.validation_report()
                issue=next(i for i in report.violations if i.element is g and i.rule==g.properties()['general'].id)
                self.assertEqual(issue.feature,'general')
                self.assertEqual(doc.resolve(issue.uri+'#'+issue.element_id),g)
                self.assertEqual(g.validate(),before)
                self.assertFalse(report.is_valid)
                json.dumps(report.to_dict())
                self.assertTrue(g.validate_detailed().violations)
                self.assertFalse(any(i in report.violations for i in report.unsupported))

    def test_cross_session_is_incomplete_context_not_violation(self):
        doc=XmiDocument.new()
        other=XmiDocument.new()
        cls=doc.create('Class')
        prop=doc.create('Property',owner=cls,feature='ownedAttribute')
        prop.type=other.create('PrimitiveType',name='String')
        report=doc.validation_report()
        warning=next(i for i in report.warnings if i.category=='cross session reference')
        self.assertEqual(warning.feature,'type')
        self.assertNotIn(warning,report.violations)
        self.assertFalse(report.complete)

    def test_known_partial_requirements_are_explicit_not_false_success(self):
        doc=XmiDocument.new()
        protocol=doc.create('ProtocolConformance')
        report=doc.validation_report()
        gaps=[i for i in report.unsupported if i.element is protocol and i.rule=='ProtocolConformance']
        self.assertEqual(len(gaps),1)
        self.assertTrue(gaps[0].cause)
        self.assertFalse(report.complete)


if __name__=='__main__':unittest.main()
