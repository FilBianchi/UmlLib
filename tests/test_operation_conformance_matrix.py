"""Version-specific operation signature oracles from the vendored OMG sources."""
import itertools
import unittest

from test_classifier_conformance_matrix import VERSIONS, facade, bounded, invariant
from umltools.xmi import XmiDocument, loads
from semantic_cases import verifies


class OperationMatrix(unittest.TestCase):
    def context(self, version):
        u = facade(version)
        doc = XmiDocument.new('Operations', semantic_version=version)
        with doc.session:
            parent, child = u.Class(name='Parent'), u.Class(name='Child')
            child.generalization.append(u.Generalization(general=parent))
            old, new = u.Operation(name='old'), u.Operation(name='new')
            parent.ownedOperation.append(old)
            child.ownedOperation.append(new)
            doc.roots[0].packagedElement.extend([parent, child])
        return u, doc, parent, child, old, new

    @verifies('Operation.isConsistentWith')
    def test_direction_type_and_multiplicity_grid(self):
        # 256 combinations per version; expectations do not call conformance
        # or multiplicity queries on the objects under test.
        for version in VERSIONS:
            u, doc, parent, child, old, new = self.context(version)
            with doc.session:
                supertype, type_, subtype, unrelated = [u.Class() for _ in range(4)]
                type_.generalization.append(u.Generalization(general=supertype))
                subtype.generalization.append(u.Generalization(general=type_))
                a, b = bounded(u, u.Parameter, 1, 2, type=type_), bounded(u, u.Parameter, 1, 2, type=type_)
                old.ownedParameter.append(a)
                new.ownedParameter.append(b)
                directions = {'in': u.ParameterDirectionKind.in_, 'out': u.ParameterDirectionKind.out,
                              'inout': u.ParameterDirectionKind.inout, 'return': u.ParameterDirectionKind.return_}
                types = {'same': type_, 'sub': subtype, 'super': supertype, 'unrelated': unrelated}
                intervals = {'equal': (1, 2), 'wider': (0, 3), 'narrower': (1, 1), 'unbounded': (0, float('inf'))}
                accepted_intervals = {'in': {'equal', 'wider', 'unbounded'},
                                      'out': {'equal', 'narrower'}, 'return': {'equal', 'narrower'},
                                      'inout': {'equal'}}
                for original_dir, replacement_dir, typed, interval in itertools.product(directions, directions, types, intervals):
                    with self.subTest(version=version, original=original_dir, replacement=replacement_dir,
                                      type=typed, interval=interval):
                        a.direction, b.direction = directions[original_dir], directions[replacement_dir]
                        b.type = types[typed]
                        b.lowerValue.value, b.upperValue.value = intervals[interval]
                        if version == '2.4.1':
                            expected = typed in ('same', 'sub')
                        else:
                            expected = (original_dir == replacement_dir and typed != 'unrelated'
                                        and interval in accepted_intervals[original_dir])
                        self.assertEqual(old.isConsistentWith(new), expected)

    @verifies('Operation.isConsistentWith')
    def test_ordering_uniqueness_flags_and_parameter_names(self):
        for version in VERSIONS:
            u, doc, parent, child, old, new = self.context(version)
            with doc.session:
                type_ = u.Class()
                a, b = u.Parameter(name='a', type=type_), u.Parameter(name='different', type=type_)
                old.ownedParameter.append(a)
                new.ownedParameter.append(b)
                for old_ordered, new_ordered, old_unique, new_unique in itertools.product((False, True), repeat=4):
                    with self.subTest(version=version, flags=(old_ordered, new_ordered, old_unique, new_unique)):
                        a.isOrdered, b.isOrdered = old_ordered, new_ordered
                        a.isUnique, b.isUnique = old_unique, new_unique
                        expected = version == '2.4.1' or (old_ordered == new_ordered and old_unique == new_unique)
                        self.assertEqual(old.isConsistentWith(new), expected)

    @verifies('Operation.isConsistentWith', 'Operation-isConsistentWith-pre')
    def test_arity_corresponding_parameter_order_and_context_repair(self):
        for version in VERSIONS:
            u, doc, parent, child, old, new = self.context(version)
            with doc.session:
                self.assertTrue(old.isConsistentWith(new))  # empty signatures
                left, right = u.Class(), u.Class()
                a, b = u.Parameter(type=left), u.Parameter(type=right)
                c, d = u.Parameter(type=left), u.Parameter(type=right)
                old.ownedParameter.extend([a, b])
                new.ownedParameter.append(c)
                self.assertFalse(old.isConsistentWith(new))
                new.ownedParameter.append(d)
                self.assertTrue(old.isConsistentWith(new))
                new.ownedParameter.reverse()
                self.assertFalse(old.isConsistentWith(new))
                new.ownedParameter.reverse()
                d.type = None
                with self.assertRaises(ValueError): old.isConsistentWith(new)
                d.type = right
                self.assertTrue(old.isConsistentWith(new))
                generalization = child.generalization[0]
                child.generalization.clear()
                with self.assertRaises(ValueError): old.isConsistentWith(new)
                child.generalization.append(generalization)
                self.assertTrue(old.isConsistentWith(new))

    @verifies('Operation.returnResult', 'Operation.at_most_one_return', 'Operation.type',
              'Operation.lower', 'Operation.upper', 'Operation.isOrdered', 'Operation.isUnique')
    def test_return_signature_mutation_and_xmi_identity(self):
        for version in VERSIONS:
            u, doc, parent, child, old, new = self.context(version)
            with doc.session:
                type_ = u.Class(name='Result')
                doc.roots[0].packagedElement.append(type_)
                ret = bounded(u, u.Parameter, 0, float('inf'), name='result', type=type_,
                              direction=u.ParameterDirectionKind.return_, isOrdered=True, isUnique=False)
                old.ownedParameter.append(ret)
                new.redefinedOperation.append(old)
                self.assertEqual((old.type, old.lower, old.upper, old.isOrdered, old.isUnique),
                                 (type_, 0, float('inf'), True, False))
                ret.direction = u.ParameterDirectionKind.out
                self.assertEqual(old.returnResult(), [])
                self.assertEqual((old.type, old.lower, old.upper, old.isOrdered, old.isUnique),
                                 (None, None, None, False, True))
                ret.direction = u.ParameterDirectionKind.return_
                extra = u.Parameter(type=type_, direction=u.ParameterDirectionKind.return_)
                old.ownedParameter.append(extra)
                self.assertFalse(invariant(version, old, 'Operation.at_most_one_return'))
                old.ownedParameter.remove(extra)
                extra.delete()
                self.assertTrue(invariant(version, old, 'Operation.at_most_one_return'))
            restored = loads(doc.dumps(), semantic_version='auto')
            named = {getattr(e, 'name', None): e for e in restored.session.elements}
            self.assertIs(named['old'].type, named['Result'])
            self.assertIs(named['result'].owner, named['old'])
            self.assertEqual(list(named['new'].redefinedOperation), [named['old']])
            self.assertEqual((named['old'].lower, named['old'].upper, named['old'].isOrdered, named['old'].isUnique),
                             (0, float('inf'), True, False))


if __name__ == '__main__':
    unittest.main()
