"""Reproducible declaration comparison of OMG UML 2.4.1 and 2.5.1.

Sources are cached, not redistributed. Text differences are review candidates,
not proofs that two OCL expressions have different meanings.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import urllib.request
import xml.etree.ElementTree as ET


def meta(node, name):
    return next((v for k,v in node.attrib.items() if k.endswith('}'+name)),None)


def kind(node): return (meta(node,'type') or '').split(':')[-1]


def compact(text): return re.sub(r'\s+',' ',text or '').strip()


def expression_text(text):
    # Preserve whitespace inside literals: 'a  b' and 'a b' differ in OCL.
    parts=re.split(r"('(?:''|[^'])*'|\"(?:\\.|[^\"\\])*\")",text or '')
    return ''.join(part if index%2 else re.sub(r'\s+',' ',part)
                   for index,part in enumerate(parts)).strip()


def inventory(path):
    root=ET.parse(path).getroot()
    parents={child:parent for parent in root.iter() for child in parent}
    ids={meta(n,'id'):n for n in root.iter() if meta(n,'id')}
    def key(node):
        if kind(node) in ('Class','Stereotype','Enumeration','PrimitiveType','Association','Extension'):
            return node.get('name') or meta(node,'id')
        parent=parents.get(node)
        if parent is None: return node.get('name') or meta(node,'id') or node.tag
        return key(parent)+'.'+(node.get('name') or meta(node,'id') or node.tag)
    def resolve(value):
        fragment=value.split('#')[-1]
        return key(ids[fragment]) if fragment in ids else fragment
    def refs(node, name):
        values=(node.get(name) or '').split()
        values.extend(meta(c,'idref') or c.get('href','') for c in node.findall(name))
        return sorted(resolve(v) for v in values if v)
    def bound(node, name):
        value=node.find(name+'Value')
        return '1' if value is None else value.get('value','0')
    def expression(node):
        return [dict(language=compact(n.get('language') or n.findtext('language')),
                     body=expression_text(n.get('body') or n.findtext('body')))
                for n in node.findall('specification')]
    def flags(node,names): return {name:node.get(name,'false') for name in names}
    result={category:{} for category in ('classes','properties','operations','rules','enumerations','associations','primitives','descriptions')}
    for node in root.iter():
        type_=kind(node); identifier=key(node)
        if not meta(node,'id'): continue  # Reference stubs are not declarations.
        if type_ in ('Class','Stereotype'):
            bases=sorted(v for g in node.findall('generalization') for v in refs(g,'general'))
            packages=[]; parent=parents.get(node)
            while parent is not None:
                if kind(parent) in ('Package','Profile'): packages.insert(0,parent.get('name'))
                parent=parents.get(parent)
            result['classes'][identifier]=dict(abstract=node.get('isAbstract','false'),leaf=node.get('isLeaf','false'),visibility=node.get('visibility','public'),bases=bases,package='::'.join(packages))
        if type_ in ('Property','ExtensionEnd'):
            default=node.find('defaultValue')
            result['properties'][identifier]=dict(type=refs(node,'type'),lower=bound(node,'lower'),upper=bound(node,'upper'),
                **flags(node,('isDerived','isDerivedUnion','isReadOnly','isOrdered','isStatic','isID')),
                isUnique=node.get('isUnique','true'),aggregation=node.get('aggregation','none'),
                visibility=node.get('visibility','public'),subsets=refs(node,'subsettedProperty'),redefines=refs(node,'redefinedProperty'),
                association=refs(node,'association'),
                default=None if default is None else dict(kind=kind(default),value=default.get('value','' if kind(default)=='LiteralString' else 'false' if kind(default)=='LiteralBoolean' else '0'),instance=refs(default,'instance')))
        if type_=='Operation':
            parameters=[dict(name=p.get('name'),type=refs(p,'type'),direction=p.get('direction','in'),
                         lower=bound(p,'lower'),upper=bound(p,'upper'),isOrdered=p.get('isOrdered','false'),isUnique=p.get('isUnique','true'))
                        for p in node.findall('ownedParameter')]
            result['operations'][identifier]=dict(parameters=parameters,visibility=node.get('visibility','public'),**flags(node,('isQuery','isStatic','isAbstract')),
                          redefines=refs(node,'redefinedOperation'),body=refs(node,'bodyCondition'),
                          preconditions=refs(node,'precondition'),postconditions=refs(node,'postcondition'))
        if type_=='Constraint':
            result['rules'][identifier]=dict(owner_kind=kind(parents[node]),expressions=expression(node),constrained=refs(node,'constrainedElement'))
        if type_=='Enumeration': result['enumerations'][identifier]=[n.get('name') for n in node.findall('ownedLiteral')]
        if type_ in ('Association','Extension'):
            result['associations'][identifier]=dict(ends=refs(node,'memberEnd'),**flags(node,('isDerived','isAbstract')))
        if type_=='PrimitiveType': result['primitives'][identifier]=dict(bases=sorted(v for g in node.findall('generalization') for v in refs(g,'general')))
        comments=[compact(c.get('body') or c.findtext('body')) for c in node.findall('ownedComment')]
        if comments and type_ in ('Class','Stereotype','Property','Operation','Constraint','PrimitiveType'):
            result['descriptions'][identifier]=hashlib.sha256('\n'.join(comments).encode()).hexdigest()
    result['raw_counts']=dict(sorted(Counter(kind(n) for n in root.iter() if kind(n)).items()))
    return result


def difference(before,after):
    shared=before.keys() & after.keys()
    changed=[]
    for key in sorted(shared):
        if before[key]!=after[key]:
            fields=sorted(k for k in before[key].keys() | after[key].keys() if before[key].get(k)!=after[key].get(k)) if isinstance(before[key],dict) else ['value']
            changed.append(dict(key=key,fields=fields,before=before[key],after=after[key]))
    return dict(before_count=len(before),after_count=len(after),added=sorted(after.keys()-before.keys()),
                removed=sorted(before.keys()-after.keys()),changed=changed)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--fetch',action='store_true')
    parser.add_argument('--cache',type=Path,default=Path('.build-tmp/version-audit'))
    args=parser.parse_args()
    manifest=json.loads(Path(__file__).with_name('uml-version-sources.json').read_text())
    sources={}
    args.cache.mkdir(parents=True,exist_ok=True)
    for source in manifest:
        path=args.cache/source['name']
        if not path.exists():
            if not args.fetch: raise FileNotFoundError(str(path)+': use --fetch')
            data=urllib.request.urlopen(source['url'],timeout=60).read()
            if hashlib.sha256(data).hexdigest()!=source['sha256']: raise ValueError('Download checksum mismatch')
            path.write_bytes(data)
        if hashlib.sha256(path.read_bytes()).hexdigest()!=source['sha256']: raise ValueError('Cache checksum mismatch: '+source['name'])
        sources[source['name']]=inventory(path)
    old=sources['UML-2.4.1.xmi'];new=sources['UML-2.5.1.xmi']
    profile_old={category:{} for category in old if category!='raw_counts'}
    for name in ('StandardProfileL2-2.4.1.xmi','StandardProfileL3-2.4.1.xmi'):
        for category in profile_old:
            for key,value in sources[name][category].items():
                if key in profile_old[category]: raise ValueError('Ambiguous profile declaration: '+key)
                profile_old[category][key]=value
    report=dict(versions=['2.4.1','2.5.1'],sources=manifest,
        scope='Merged L3 metamodel, PrimitiveTypes, combined L2/L3 StandardProfile declarations. Text changes require semantic/prose review; package relocation is separate from structure.',
        metamodel={category:difference(old[category],new[category]) for category in old if category!='raw_counts'},
        standard_profile={category:difference(profile_old[category],sources['StandardProfile-2.5.1.xmi'][category]) for category in profile_old},
        primitive_types=difference(sources['PrimitiveTypes-2.4.1.xmi']['primitives'],sources['PrimitiveTypes-2.5.1.xmi']['primitives']),
        raw_counts={name:value['raw_counts'] for name,value in sources.items()},
        vendored_251_matches=inventory(Path('umltools/data/UML.xmi'))==new)
    Path('uml-version-comparison.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    for category,delta in report['metamodel'].items():
        print(category,delta['before_count'],delta['after_count'],'added',len(delta['added']),'removed',len(delta['removed']),'changed',len(delta['changed']))


if __name__=='__main__':main()
