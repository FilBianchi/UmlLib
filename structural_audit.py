"""Structural declaration inventory and clearly scoped runtime evidence."""
import json
from pathlib import Path
from collections import Counter
from semantic_report import report
from umltools import SPECIFICATIONS, ENUMERATIONS


FAMILY_EXAMPLES = {
    'bounded collection': ['test_structural_contracts.StructuralContractCases.test_unique_bounds_order_bags_and_atomic_collection_operations'],
    'nonunique collection': ['test_structural_contracts.StructuralContractCases.test_unique_bounds_order_bags_and_atomic_collection_operations'],
    'composite': ['test_structural_contracts.StructuralContractCases.test_composite_reparenting_aliases_cycle_and_constructor_rollback'],
    'subset': ['test_structural_contracts.StructuralContractCases.test_multiple_subset_witnesses_superset_removal_and_failure_rollback'],
    'redefinition': ['test_structural_contracts.StructuralContractCases.test_redefinition_stored_superset_and_derived_union_write_protection',
                     'test_structural_contracts.StructuralContractCases.test_multiple_subset_witnesses_superset_removal_and_failure_rollback'],
    'derived': ['test_structural_contracts.StructuralContractCases.test_redefinition_stored_superset_and_derived_union_write_protection'],
    'association': ['test_structural_contracts.StructuralContractCases.test_noncomposite_inverse_reassignment_and_clear_from_both_ends',
                    'test_structural_contracts.StructuralContractCases.test_stored_many_to_many_inverses_and_transactional_invalid_edit',
                    'test_structural_contracts.StructuralContractCases.test_cross_session_reference_diagnostics_inverse_links_and_deletion'],
}


def audit():
    matrix = report()
    properties = [r for r in matrix['definitions'] if r['kind'] in ('structural property','derived property','association-owned property')]
    known_ids = {r['id'] for r in properties}
    known_types = set(SPECIFICATIONS) | set(ENUMERATIONS) | {'Boolean','Integer','Real','String','UnlimitedNatural'}
    entries, diagnostics = [], []
    for record in properties:
        identifier = record['id']
        if record['type'] not in known_types: diagnostics.append(dict(id=identifier, issue='unknown type', target=record['type']))
        for relation in ('subsets', 'redefines'):
            for target in record.get(relation, ()):
                if target not in known_ids: diagnostics.append(dict(id=identifier, issue='unresolved '+relation, target=target))
        if record['lower'] < 0 or record['upper'] is not None and record['upper'] < record['lower']:
            diagnostics.append(dict(id=identifier, issue='invalid bounds'))
        families = []
        if record['upper'] is not None and record['upper'] > 1: families.append('bounded collection')
        if not record['unique']: families.append('nonunique collection')
        if record['aggregation'] == 'composite': families.append('composite')
        if record.get('subsets'): families.append('subset')
        if record.get('redefines'): families.append('redefinition')
        if record['kind'] == 'derived property': families.append('derived')
        if record.get('association'): families.append('association')
        entries.append(dict(id=identifier, package=record['package'], kind=record['kind'], source=record['source'],
                            type=record['type'], lower=record['lower'], upper=record['upper'], ordered=record['ordered'],
                            unique=record['unique'], aggregation=record['aggregation'], families=families,
                            subsets=record.get('subsets',()), redefines=record.get('redefines',()),
                            declaration_sweeps=record.get('structural_sweeps', []),
                            definition_examples=record['tests'],
                            family_examples=sorted({test for family in families for test in FAMILY_EXAMPLES[family]}),
                            evidence_scope='Declaration sweeps check defaults, rejection of wrong types and one declared-type setter value. Family examples demonstrate representative relationships only; they do not certify every association/subset/redefinition/prose requirement.'))
    return dict(scope='All 950 declared property/end records, with metadata reference/bounds checks and explicit evidence scopes. Association-owned ends have no generated direct setters and are not counted in stored-setter sweeps.',
                counts=dict(Counter(r['kind'] for r in entries)), families=dict(Counter(f for r in entries for f in r['families'])),
                declaration_diagnostics=diagnostics, properties=entries,
                session_policy='Cross-session references remain allowed and transactionally updated/cleaned. validate reports cross session reference on stored links; allInstances-based queries remain scoped to each element extent.',
                remaining='Per-association/end behavior, all positive subtype/default combinations, arbitrary mutation sequences, broader normative prose and a complete XMI/serialization contract remain open.')


def write_audit():
    result = audit()
    root = Path(__file__).parent
    root.joinpath('structural-audit.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    lines = ['# Structural contract audit', '', result['scope'], '', '| Definition kind | Count |', '| --- | --- |']
    for kind, count in result['counts'].items(): lines.append(f'| {kind} | {count} |')
    lines.extend(['', 'The 549 stored declarations receive default/wrong-type and declared-type assignment sweeps. Metadata diagnostics: '+str(len(result['declaration_diagnostics']))+'.', '',
                  'Family examples cover uniqueness/order/bags, bounds, composites, inverse rebinding, subset witnesses, stored redefinitions, rollback, derived-write protection, cross-session links and cached collections after deletion.', '',
                  result['session_policy'], '', 'Detailed per-definition links and their evidence scope are in `structural-audit.json`. Regenerate with `python structural_audit.py`.', '', result['remaining']])
    root.joinpath('STRUCTURAL_AUDIT.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(json.dumps(dict(counts=result['counts'], declaration_diagnostics=len(result['declaration_diagnostics']))))


if __name__ == '__main__': write_audit()
