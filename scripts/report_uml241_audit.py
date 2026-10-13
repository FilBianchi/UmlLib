"""Inventory the audited 2.4.1 CommonStructure/Values scope, without conflating versions."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from importlib import import_module
import Uml241


def main():
    engine=Uml241._engine
    specification=import_module(engine.__name__+'.specification')
    names=sorted(set(Uml241.CommonStructure.__all__+Uml241.Values.__all__+['Package']))
    records=[]
    for name in names:
        spec=engine.SPECIFICATIONS.get(name)
        if spec is None:continue
        for operation,xml in spec.operations.items():
            node=ET.fromstring(xml)
            identifier=name+'.'+operation
            records.append(dict(kind='operation',identifier=identifier,
                source='umltools/data/UML-2.4.1.xmi#'+node.get(specification.XMI+'id'),
                implementation='native Python' if identifier in engine.native.OPERATIONS else 'unsupported',
                conditions=[dict(name=r.get('name'),expressions=list(specification.expression(r))) for r in node.findall('ownedRule')]))
        for constraint,expressions in spec.constraints.items():
            identifier=name+'.'+constraint
            records.append(dict(kind='constraint',identifier=identifier,
                source='umltools/data/UML-2.4.1.xmi#'+name+'-'+constraint,
                implementation='native Python' if identifier in engine.native.CONSTRAINTS else 'unsupported',expressions=list(expressions)))
        for prop in spec.properties.values():
            if prop.flags.get('isDerived')!='true':continue
            mechanism='native Python' if prop.id in engine.native.DERIVATIONS else 'structural intrinsic' if prop.id in ('Element-owner','Element-ownedElement','NamedElement-namespace') else 'structural union' if prop.flags.get('isDerivedUnion')=='true' else 'query' if prop.name in spec.operations and name+'.'+prop.name in engine.native.OPERATIONS else 'unsupported'
            records.append(dict(kind='derived property',identifier=prop.id,
                source='umltools/data/UML-2.4.1.xmi#'+prop.id,implementation=mechanism))
    report=dict(version='2.4.1',scope=names,limitations=[
        'Registration is not exhaustive semantic conformance. Remaining package audits are recorded in UML241_AUDIT.md; general expression evaluation requires explicit evidence.',
        'Generic supplemental prose validation and migration remain unsupported for 2.4.1; typed runtime profiles and XMI exchange are documented in PROFILE_RUNTIME_241.md and XMI241_SUPPORT.md.',
        'Malformed/pseudo-body formulas are interpreted through their normative ownedComment; decisions are listed in UML241_COMMON_VALUES_AUDIT.md.'],
        enabled_operations=len(engine.native.OPERATIONS),enabled_constraints=len(engine.native.CONSTRAINTS),records=records)
    Path('uml241-common-values-audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    from collections import Counter
    print(dict(Counter((r['kind'],r['implementation']) for r in records)))


if __name__=='__main__':main()
