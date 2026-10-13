"""Check meaningful normalization across the two normative XMI encodings."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from scripts.compare_uml_versions import inventory,difference,expression_text


class ComparisonCases(unittest.TestCase):
    def test_ocl_literal_whitespace_is_not_erased(self):
        self.assertNotEqual(expression_text("self.name = 'a  b'"),expression_text("self.name = 'a b'"))
        self.assertEqual(expression_text("self.name  =\n 'a  b'"),"self.name = 'a  b'")

    def read(self,body,namespace='20100901'):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'model.xmi'
            path.write_text(f'<x:XMI xmlns:x="http://www.omg.org/spec/XMI/{namespace}" xmlns:u="urn:uml">{body}</x:XMI>',encoding='utf-8')
            return inventory(path)

    def test_reference_encodings_and_ids_do_not_create_false_differences(self):
        old=self.read('<packagedElement x:type="u:Class" x:id="C" name="C"><ownedAttribute x:type="u:Property" x:id="p" name="p" type="C" subsettedProperty="q"/><ownedAttribute x:type="u:Property" x:id="q" name="q" type="C"/></packagedElement>')
        new=self.read('<packagedElement x:type="u:Class" x:id="other" name="C"><ownedAttribute x:type="u:Property" x:id="newp" name="p"><type x:idref="other"/><subsettedProperty x:idref="newq"/></ownedAttribute><ownedAttribute x:type="u:Property" x:id="newq" name="q"><type x:idref="other"/></ownedAttribute></packagedElement>','20131001')
        self.assertEqual(old,new)

    def test_reference_stubs_are_not_class_declarations(self):
        result=self.read('<packagedElement x:type="u:Class" x:id="C" name="C"/><reference x:type="u:Class" href="elsewhere#Class"/>')
        self.assertEqual(list(result['classes']),['C'])

    def test_missing_lower_literal_value_means_zero_not_one(self):
        old=self.read('<packagedElement x:type="u:Class" x:id="C" name="C"><ownedAttribute x:type="u:Property" x:id="p" name="p"><lowerValue x:type="u:LiteralInteger" x:id="l"/></ownedAttribute></packagedElement>')
        self.assertEqual(old['properties']['C.p']['lower'],'0')
        self.assertEqual(old['properties']['C.p']['upper'],'1')

    def test_rule_whitespace_and_attribute_text_are_normalized(self):
        template='<packagedElement x:type="u:Class" x:id="C" name="C"><ownedRule x:type="u:Constraint" x:id="r" name="valid"><specification {}/></ownedRule></packagedElement>'
        old=self.read(template.format('language="OCL" body="self = self"'))
        new=self.read('<packagedElement x:type="u:Class" x:id="C" name="C"><ownedRule x:type="u:Constraint" x:id="r" name="valid"><specification><language>OCL</language><body>self  =\n self</body></specification></ownedRule></packagedElement>')
        self.assertEqual(difference(old['rules'],new['rules'])['changed'],[])
