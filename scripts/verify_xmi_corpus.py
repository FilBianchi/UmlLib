"""Verify pinned public models. Fetching is explicit; ordinary XMI loading is offline."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import urllib.request
from importlib import import_module


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--fetch',action='store_true')
    parser.add_argument('--complex',action='store_true',help='Include Eclipse with its Ecore/Standard dependencies; unsupported vendor values are diagnosed and retained.')
    parser.add_argument('--semantic-version',choices=('2.4.1','2.5.1'),default='2.5.1',help='Select actual Python metamodel semantics; Eclipse dialect URIs alone are ambiguous.')
    parser.add_argument('--cache',type=Path,default=Path('.build-tmp/xmi-corpus'))
    options=parser.parse_args()
    if options.complex and options.semantic_version=='2.4.1':parser.error('The complex runtime-profile corpus is only supported by the 2.5.1 backend')
    exchange=import_module('Uml241.xmi' if options.semantic_version=='2.4.1' else 'Uml251.xmi')
    load,loads,dumps=exchange.load,exchange.loads,exchange.dumps
    report_name='report.json' if options.semantic_version=='2.5.1' else 'report-2.4.1.json'
    manifest=json.loads(Path(__file__).with_name('xmi-corpus.json').read_text())
    options.cache.mkdir(parents=True,exist_ok=True)
    for entry in manifest:
        path=options.cache/entry['name']
        if not path.exists():
            if not options.fetch: raise FileNotFoundError(f'{path}: use --fetch to download pinned sources')
            data=urllib.request.urlopen(entry['url'],timeout=60).read()
            if hashlib.sha256(data).hexdigest()!=entry['sha256']: raise ValueError('Download checksum mismatch: '+entry['name'])
            path.write_bytes(data)
        if hashlib.sha256(path.read_bytes()).hexdigest()!=entry['sha256']: raise ValueError('Cache checksum mismatch: '+entry['name'])
    cache=options.cache
    resources={'http://www.eclipse.org/uml2/5.0.0/UML/Profile/Standard':cache/'Standard.profile.uml',
               'http://www.eclipse.org/uml2/5.0.0/UML':cache/'UML.metamodel.uml'}
    for group,names in [('UML_LIBRARIES',['UMLPrimitiveTypes.library.uml','EcorePrimitiveTypes.library.uml']),
                        ('UML_METAMODELS',['UML.metamodel.uml','Ecore.metamodel.uml']),
                        ('UML_PROFILES',['Standard.profile.uml','Ecore.profile.uml'])]:
        for name in names: resources['pathmap://'+group+'/'+name]=cache/name
    cases=['simple-machine.uml','simple-submachine.uml','ordershipping.uml','multijoin-forkjoin.uml','linked-regions.uml']
    if options.complex: cases+=['Bug497359.uml','UML.metamodel.uml']
    result=[]
    for name in cases:
        permissive=name in ('Bug497359.uml','UML.metamodel.uml')
        doc=load(cache/name,resources=resources,strict=not permissive)
        print(f'{name}: import finished ({len(doc.session.elements)} objects); checking export and reimport',flush=True)
        data=dumps(doc);restored=loads(data,strict=not permissive)
        # Compare decoded graph counts plus normalization of known features.
        counts=Counter(o.__spec__.name for o in doc.session.elements)
        assert counts==Counter(o.__spec__.name for o in restored.session.elements),name+': metaclass counts changed'
        assert len(doc.runtime_values)==len(restored.runtime_values),name+': runtime instance count changed'
        known=dumps(restored.roots)
        assert known==dumps(loads(known,strict=not permissive).roots),name+': known graph changed during round trip'
        row=dict(name=name,semantic_version=doc.semantic_version,mode='permissive' if permissive else 'strict',objects=sum(counts.values()),
                 metaclasses=dict(sorted(counts.items())),runtime_values=len(doc.runtime_values),complete=doc.complete,
                 diagnostics=[dict(code=d.code,feature=d.feature,message=d.message) for d in doc.diagnostics],
                 source=next(e for e in manifest if e['name']==name))
        result.append(row)
        (cache/report_name).write_text(json.dumps(result,indent=2)+'\n')
        print(f'{name}: {row["objects"]} UML objects, {row["runtime_values"]} profile values, {len(row["diagnostics"])} diagnostics; round trip passed',flush=True)
    print('Public corpus verified; details in '+str(cache/report_name))


if __name__=='__main__': main()
