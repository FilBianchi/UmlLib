"""All 550 stored 2.4.1 declarations plus independent structural contract families."""
import unittest
import Uml241 as U
from Uml241._runtime import engine


def concrete(owner,identifier=None):
    registry=U.Class.__registry__
    candidates=[cls for cls in registry.values() if isinstance(cls,type) and hasattr(cls,'__spec__')
        and not cls.__spec__.abstract and issubclass(cls,registry[owner])
        and (identifier is None or any(p.id==identifier for p in cls.properties().values()))]
    return min(candidates,key=lambda c:(len(c.__mro__),c.__spec__.name)) if candidates else None


class Structural241Cases(unittest.TestCase):
    def setUp(self):
        self.session=U.ModelSession();self.session.__enter__()
        self.addCleanup(self.session.__exit__,None,None,None)

    def test_every_stored_declaration_defaults_and_atomic_wrong_type_rejection(self):
        checked=set();hidden=set()
        for spec in engine.SPECIFICATIONS.values():
            for prop in spec.properties.values():
                if prop.flags.get('isDerived')=='true':continue
                with self.subTest(property=prop.id):
                    cls=concrete(spec.name,prop.id)
                    if cls is None:hidden.add(prop.id);continue
                    obj=cls();previous=getattr(obj,prop.name)
                    many=prop.upper is None or prop.upper>1
                    if many:self.assertEqual(list(previous),[])
                    elif prop.default is None:self.assertIsNone(previous)
                    else:engine.validate_item(obj,previous,prop.type)
                    with self.assertRaises(TypeError):setattr(obj,prop.name,[object()] if many else object())
                    self.assertIs(getattr(obj,prop.name),previous)
                    checked.add(prop.id)
        self.assertEqual(hidden,{'StructuralFeature-isReadOnly'})
        self.assertEqual(len(checked),549)

    def test_every_stored_setter_accepts_its_declared_type(self):
        primitives={'Boolean':True,'Integer':1,'Real':1.5,'UnlimitedNatural':2,'String':'audit'}
        registry=U.Class.__registry__;checked=set();hidden=set()
        for spec in engine.SPECIFICATIONS.values():
            for prop in spec.properties.values():
                if prop.flags.get('isDerived')=='true':continue
                with self.subTest(property=prop.id):
                    cls=concrete(spec.name,prop.id)
                    if cls is None:hidden.add(prop.id);continue
                    obj=cls()
                    if prop.type in primitives:value=primitives[prop.type]
                    elif hasattr(registry[prop.type],'__spec__'):value=concrete(prop.type)()
                    else:value=next(iter(registry[prop.type]))
                    many=prop.upper is None or prop.upper>1
                    setattr(obj,prop.name,[value] if many else value)
                    actual=getattr(obj,prop.name)
                    if many:self.assertEqual(list(actual),[value])
                    else:self.assertEqual(actual,value)
                    checked.add(prop.id)
        self.assertEqual(hidden,{'StructuralFeature-isReadOnly'})
        self.assertEqual(len(checked),549)

    def test_subset_inverse_redefinition_and_cached_collections(self):
        node=U.StructuredActivityNode();first,second=U.Activity(),U.Activity()
        node.activity=first
        self.assertIn(node,first.node);self.assertIn(node,first.group)
        self.assertIs(node.activity,first)
        with self.assertRaises(ValueError):second.node.append(node)
        self.assertEqual(list(second.node),[])
        node.activity=second
        self.assertEqual(list(first.node),[]);self.assertEqual(list(first.group),[])
        self.assertIn(node,second.node);self.assertIn(node,second.group)
        node.activity=None
        self.assertEqual(list(second.node),[]);self.assertEqual(list(second.group),[])
        self.assertIsNone(node.owner)
        parameter=U.Parameter();operation=U.Operation(ownedParameter=[parameter])
        self.assertEqual(list(operation.uml_operation('Element','allOwnedElements')),[parameter])
        relations=U.GeneralizationSet();generalization=U.Generalization(generalizationSet=[relations])
        self.assertIn(generalization,relations.generalization)
        cached=relations.generalization
        with self.assertRaises(TypeError):cached[:]=['wrong']
        self.assertEqual(list(cached),[generalization])
        operation.delete()
        self.assertTrue(parameter.is_deleted)

    def test_port_deletion_restrict_is_atomic_and_composite_cycles_fail(self):
        port=U.Port();connector=U.Connector(end=[U.ConnectorEnd(role=port)])
        owner=U.Class(ownedAttribute=[port],ownedConnector=[connector])
        observer=U.InformationFlow(informationSource=[port])
        with self.assertRaises(U.DeletionRestrictedError):port.delete(on_references='restrict')
        self.assertFalse(port.is_deleted);self.assertFalse(connector.is_deleted)
        self.assertEqual(list(observer.informationSource),[port])
        port.delete()
        self.assertTrue(connector.is_deleted)
        self.assertEqual(list(observer.informationSource),[])
        outer,inner=U.Package(),U.Package()
        outer.packagedElement.append(inner)
        with self.assertRaises(ValueError):inner.packagedElement.append(outer)
        self.assertIs(inner.owner,outer);self.assertIsNone(outer.owner)
