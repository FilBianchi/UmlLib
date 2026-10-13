"""Reproducible inventory of all 2.4.1 declarations and scoped audit evidence."""
from collections import Counter
from importlib import import_module
from pathlib import Path
import json
import xml.etree.ElementTree as ET

import Uml241
from umltools import SPECIFICATIONS as layout
from semantic_report import AUDIT_LIMITS, CONTEXT_LIMITS, PARTIAL

ROOT=Path(__file__).resolve().parents[1]


def audit():
    engine=Uml241._engine
    source=import_module(engine.__name__+'.specification')
    tree=ET.parse(ROOT/'umltools/data/UML-2.4.1.xmi').getroot()
    nodes={node.get(source.XMI+'id'):node for node in tree.iter() if node.get(source.XMI+'id')}
    records=[];properties=[];diagnostics=[]
    declared_operations=set();declared_constraints=set()
    known_types=set(engine.SPECIFICATIONS)|set(engine.ENUMERATIONS)|{'Boolean','Integer','Real','String','UnlimitedNatural'}
    property_ids={identifier for identifier,node in nodes.items() if node.get(source.XMI+'type')=='uml:Property'}

    def implementation(function):
        return function.__module__+'.'+function.__qualname__ if function else None

    for name,spec in sorted(engine.SPECIFICATIONS.items()):
        family=layout[name].package
        for operation,xml in sorted(spec.operations.items()):
            identifier=name+'.'+operation;declared_operations.add(identifier)
            node=ET.fromstring(xml)
            records.append(dict(kind='operation',identifier=identifier,family=family,
                source='umltools/data/UML-2.4.1.xmi#'+node.get(source.XMI+'id'),
                source_description=[c.findtext('body','') for c in node.findall('ownedComment')],
                expressions=list(source.expression(node)),
                conditions=[dict(name=r.get('name'),expressions=list(source.expression(r))) for r in node.findall('ownedRule')],
                implementation=implementation(engine.native.OPERATIONS.get(identifier)),
                reviewed_shared_implementation=identifier in engine.AUDIT_REUSE['operations'],
                decision=engine.AUDIT_DECISIONS.get(identifier,'reviewed shared implementation' if identifier in engine.AUDIT_REUSE['operations'] else 'version-specific implementation'),
                shared_source_caveat=AUDIT_LIMITS.get(identifier)))
        for constraint,expressions in sorted(spec.constraints.items()):
            identifier=name+'.'+constraint;declared_constraints.add(identifier)
            node=nodes[name+'-'+constraint]
            records.append(dict(kind='constraint',identifier=identifier,family=family,
                source='umltools/data/UML-2.4.1.xmi#'+node.get(source.XMI+'id'),
                source_description=[c.findtext('body','') for c in node.findall('ownedComment')],
                expressions=list(expressions),implementation=implementation(engine.native.CONSTRAINTS.get(identifier)),
                reviewed_shared_implementation=identifier in engine.AUDIT_REUSE['constraints'],
                scope='lifecycle event; static evaluation requires history' if identifier=='Port.port_destroyed' else 'model predicate; external evidence may be required',
                shared_source_caveat=AUDIT_LIMITS.get(identifier),contextual_limit=CONTEXT_LIMITS.get(identifier)))
        for prop in spec.properties.values():
            if prop.flags.get('isDerived')!='true':continue
            mechanism='native Python' if prop.id in engine.native.DERIVATIONS else 'structural intrinsic' if prop.id in ('Element-owner','Element-ownedElement','NamedElement-namespace') else 'structural union' if prop.flags.get('isDerivedUnion')=='true' else 'query' if prop.name in spec.operations and name+'.'+prop.name in engine.native.OPERATIONS else 'unsupported'
            records.append(dict(kind='derived property',identifier=prop.id,family=family,
                source='umltools/data/UML-2.4.1.xmi#'+prop.id,implementation=mechanism))
    parents={child:parent for parent in tree.iter() for child in parent}
    for identifier in sorted(property_ids):
        node=nodes[identifier];owner=parents[node]
        type_=source.reference(node,'type');lower=node.find('lowerValue');upper=node.find('upperValue')
        low=1 if lower is None else int(lower.get('value','0'))
        high='1' if upper is None else upper.get('value','0')
        high=None if high=='*' else int(high)
        subsets=source.references(node,'subsettedProperty');redefines=source.references(node,'redefinedProperty')
        kind='association-owned property' if owner.get(source.XMI+'type')=='uml:Association' else 'derived property' if node.get('isDerived')=='true' else 'stored property'
        if type_ not in known_types:diagnostics.append(dict(id=identifier,issue='unknown type',target=type_))
        for relation,targets in (('subsets',subsets),('redefines',redefines)):
            for target in targets:
                if target not in property_ids:diagnostics.append(dict(id=identifier,issue='unresolved '+relation,target=target))
        if low<0 or high is not None and high<low:diagnostics.append(dict(id=identifier,issue='invalid bounds'))
        properties.append(dict(id=identifier,kind=kind,type=type_,lower=low,upper=high,
            ordered=node.get('isOrdered','false')=='true',unique=node.get('isUnique','true')=='true',
            aggregation=node.get('aggregation','none'),association=node.get('association'),subsets=subsets,redefines=redefines,
            source='umltools/data/UML-2.4.1.xmi#'+identifier,
            setter_sweep=kind=='stored property' and identifier!='StructuralFeature-isReadOnly'))
    missing_ops=sorted(declared_operations-set(engine.native.OPERATIONS))
    missing_rules=sorted(declared_constraints-set(engine.native.CONSTRAINTS))
    extra_ops=sorted(set(engine.native.OPERATIONS)-declared_operations)
    extra_rules=sorted(set(engine.native.CONSTRAINTS)-declared_constraints)
    missing_derived=[r['identifier'] for r in records if r['kind']=='derived property' and r['implementation']=='unsupported']
    counts=dict(Counter(r['kind'] for r in records))
    assert counts=={'operation':150,'constraint':433,'derived property':74},counts
    assert not (missing_ops or missing_rules or extra_ops or extra_rules or missing_derived or diagnostics)
    families={family:dict(Counter(r['kind'] for r in records if r['family']==family)) for family in sorted({r['family'] for r in records})}
    test_files=['test_uml241_common_values.py','test_uml241_remaining.py','test_uml241_structural.py','test_version_backends.py']
    return dict(version='2.4.1',counts=counts,families=families,
        structural_counts=dict(Counter(p['kind'] for p in properties)),declaration_diagnostics=diagnostics,
        missing_operations=missing_ops,missing_constraints=missing_rules,missing_derivations=missing_derived,
        extraneous_operations=extra_ops,extraneous_constraints=extra_rules,
        hidden_stored_declarations={'StructuralFeature-isReadOnly':'Redefined by Property.isReadOnly on every concrete subtype; metadata checked, no direct effective setter.'},
        stored_setters_swept=sum(p['setter_sweep'] for p in properties),
        evidence_scope='All declarations inventoried; 549 effective setters receive defaults/wrong-type/declared-type sweeps. Family scenarios are representative, not one proof per invariant or every association/mutation sequence.',
        test_files=['tests/'+p for p in test_files],
        supplemental_helpers=[owner+'.'+name for owner,name in sorted(engine.UmlElement.__supplemental_operations__)],
        supplemental_helper_scope='Internal dependency queries, not additional normative 2.4.1 operation declarations.',
        limitations=[
            'Registration and declaration audits are not UML conformance certification.',
            'Generic supplemental normative prose remains unsupported (UML2.4.1.prose); execution traces, PackageMerge reconciliation and behavioral protocol-conformance proof are not supplied.',
            'Opaque expression evaluation, foreign lexical default representations and domain collection types require explicit adapters/facts.',
            'Activity autonomy, relative TimeEvent starting times, conditional trigger assignment and transformation Behavior purity require trusted facts when the model cannot establish them.',
            'Core XMI 2.4.1 exchange is implemented in 0.18.0 (XMI241_SUPPORT.md); runtime profile applications, CMOF/vendor adapters and migration remain separate unsupported contracts.',
            'Implicit region/machine extension preserves original structure by reference; it does not clone inherited composite members into the extension.',
            'Connector feature compatibility is the documented nominal/signature interpretation; trace conformance and arbitrary execution are not proved.',
        ],shared_reference_caveats={key:value for key,value in PARTIAL.items() if key.split('-')[0] in engine.SPECIFICATIONS and key not in ('DeploymentTarget-deployedElement','DeploymentSpecification-deployed_elements')},
        shared_reference_caveat_scope='Inherited project limitations of shared algorithms; source-body descriptions refer to the 2.5.1 reference audit and must be read alongside the separate 2.4.1 decisions.',
        records=records,properties=properties)


def main():
    result=audit()
    (ROOT/'uml241-audit.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({key:result[key] for key in ('counts','structural_counts','stored_setters_swept','declaration_diagnostics')}))


if __name__=='__main__':main()
