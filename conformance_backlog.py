"""Operational census of known limitations, not a census of all normative prose."""
import json
from pathlib import Path
from collections import Counter
from semantic_report import report


def backlog():
    matrix = report()
    entries = []
    for record in matrix['definitions']:
        review = record['review']
        if review not in ('partial', 'context dependent', 'source inconsistency'): continue
        if review == 'source inconsistency':
            priority, area, action = 'P0', 'source policy', 'Compare the preserved body/description, document the chosen policy and resolve normative equivalence before a conformity claim.'
        elif review == 'context dependent':
            priority, area, action = 'P1', 'context adapters', 'Specify the required numeric, reference, purity, collection-type or endpoint evidence; keep unknowns unsupported and test adapter lifecycle.'
        elif record['package'] in ('Packages', 'StructuredClassifiers'):
            priority, area, action = 'P1', 'profiles and package merge', 'Implement the documented missing profile/tagged-value/strictness or merge contract with independent behavioral examples.'
        else:
            priority, area, action = 'P0', 'static semantics', 'Decompose the remaining limitation into represented static checks and external evidence; implement only the represented portion and preserve explicit unknowns.'
        if record['id'] in ('ObjectNode-input_output_parameter', 'ObjectFlow-input_and_output_parameter', 'ObjectFlow-transformation_behavior'):
            priority, area, action = 'P1', 'behavior evidence', 'Define a trusted Behavior purity analyzer contract and deletion/extent lifecycle; type correspondence is already checked in the represented cases.'
        if record['id'].startswith('DecisionNode-') and record['static_supplements']:
            priority, area, action = 'P1', 'token-type evidence', 'Preserve unsupported for untyped/cyclic-only paths and specify external token-type evidence if needed; represented ordered input types are implemented.'
        if record['id'] in ('DeploymentTarget-deployedElement','DeploymentSpecification-deployed_elements'):
            action = 'Resolve nested/inherited Artifact and slot-based manifestation requirements against normative sources; direct modeled Artifact instances are supported by the supplemental resolver.'
        if record['id'] == 'Message-signature_is_operation_reply':
            priority, area, action = 'P0', 'source policy', 'Review the XMI/prose policy for reply argument representation; typed direct values, first expression operands and wildcards are checked by the supplement.'
        if record['id'] in ('Stereotype','ProfileApplication-isStrict'):
            action = 'Extend implemented typed profile values, navigable binary links and strict views with explicit custom-value/derived-expression adapters, non-navigable runtime navigation, non-UML metaclasses and exchange contracts; preserve unsupported external languages.'
        entries.append(dict(id=record['id'], name=record.get('name', record['id']), package=record['package'],
                            priority=priority, area=area, status=review, limitation=record['limitation'],
                            source=record['source'], next_action=action, static_supplements=record['static_supplements']))
    entries.sort(key=lambda r: (r['priority'], r['area'], r['package'], r['id']))
    supplemental = [dict(id=r['id'], source=r['source'], tests=r['tests'], verification=r['verification'])
                    for r in matrix['definitions'] if r['kind'].startswith('supplemental')]
    return dict(scope='Known limitations explicitly recorded in the semantic matrix. Additional normative prose and structural metadata need separate requirement decomposition; this is not a complete UML requirement census.',
                priorities=dict(Counter(r['priority'] for r in entries)), known_limitations=entries,
                supplemental_checks=supplemental,
                remaining_workstreams=[
                    dict(priority='P0', area='structural contracts', action='Extend STRUCTURAL_AUDIT.md declaration sweeps/family scenarios to per-association/end semantics, subtype combinations and broader mutation sequences; cross-session references are allowed but diagnosed.'),
                    dict(priority='P0', area='additional prose', action='Decompose the 242 class descriptions and additional normative prose into atomic requirements; counts of XMI definitions alone cannot close this scope.'),
                    dict(priority='P1', area='profiles', action='Typed tags, binary navigable associations, strict views and trusted user-constraint integration are implemented. Complete custom value/expression adapters, non-navigable navigation, non-UML metaclasses and CMOF/exchange semantics.'),
                    dict(priority='P1', area='exchange', action='Core/profile graph exchange and generic typed lexical primitive values are implemented. Extend MIWG samples, default/derived evaluators, CMOF and vendor reference/layout adapters; keep decoding distinct from UML validation.'),
                    dict(priority='P1', area='UML versions', action='Uml241/Uml251 provide independent metamodels and isolated state. CommonStructure/Values 2.4.1 is audited in UML241_COMMON_VALUES_AUDIT.md; next audit Classification/SimpleClassifiers and remaining families/prose, then profile/XMI contracts and loss-aware migration fixtures. 2.5 is not a target.'),
                    dict(priority='P2', area='diagram exchange', action='Implement StandardProfile/UMLDI and preserve diagram metadata separately from core model semantics.')])


def write_backlog():
    result = backlog()
    root = Path(__file__).parent
    root.joinpath('conformance-backlog.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    lines = ['# Known conformance work', '', result['scope'], '',
             'Generated by `python conformance_backlog.py`; detailed sources, limitations and next actions are in `conformance-backlog.json`.', '',
             '## Remaining workstreams', '', '| Priority | Area | Next action |', '| --- | --- | --- |']
    for item in result['remaining_workstreams']:
        lines.append('| '+ ' | '.join(item[k] for k in ('priority','area','action'))+' |')
    lines.extend(['', '## Supplemental static checks implemented', '', '| Identifier | Linked examples |', '| --- | --- |'])
    for item in result['supplemental_checks']: lines.append('| '+item['id']+' | '+str(len(item['tests']))+' |')
    lines.extend(['', '## Known limitations to resolve', '', '| Priority | Area | Source definition | Status |', '| --- | --- | --- | --- |'])
    for item in result['known_limitations']:
        lines.append('| '+' | '.join(item[k] for k in ('priority','area','id','status'))+' |')
    root.joinpath('CONFORMANCE_BACKLOG.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(json.dumps(dict(priorities=result['priorities'], supplemental_checks=len(result['supplemental_checks']))))


if __name__ == '__main__': write_backlog()
