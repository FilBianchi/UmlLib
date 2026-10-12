"""UML XMI graph exchange. No network access, OCL execution or vendor guessing.

load/loads return a document with an isolated extent, resource-scoped identities and
explicit diagnostics. dump/dumps serialize stored features, not derived caches.
"""
from dataclasses import dataclass
from enum import Enum
from io import BytesIO
from pathlib import Path
from urllib.parse import urljoin, urldefrag, urlparse, unquote, urlsplit, urlunsplit
import copy
import re
import xml.etree.ElementTree as ET

XMI_NS = 'http://www.omg.org/spec/XMI/20131001'
UML_NS = 'http://www.omg.org/spec/UML/20161101'
LIB_NS = 'urn:umllib:xmi:1'
XSI_NS = 'http://www.w3.org/2001/XMLSchema-instance'
XMI_NAMESPACES = {XMI_NS, 'http://www.omg.org/XMI', 'http://www.omg.org/spec/XMI/20110701', 'http://www.omg.org/spec/XMI/20161101'}
UML_NAMESPACES = {UML_NS, 'http://www.omg.org/spec/UML/20131001', 'http://www.omg.org/spec/UML/20110701',
                  'http://www.omg.org/spec/UML/20090901', 'http://www.eclipse.org/uml2/3.0.0/UML',
                  'http://www.eclipse.org/uml2/4.0.0/UML', 'http://www.eclipse.org/uml2/5.0.0/UML'}


def _split(name):
    if name.startswith('{'): return tuple(name[1:].split('}', 1))
    return '', name


def _meta(node, local):
    return next((value for key, value in node.attrib.items() if _split(key)[0] in XMI_NAMESPACES and _split(key)[1] == local), None)


def _absolute(uri, reference):
    if reference.startswith('#'): return urldefrag(uri)[0]+reference
    if urlparse(reference).scheme: return reference
    parsed=urlsplit(uri)
    if parsed.scheme not in ('http','https','file','ftp'):
        joined=urlsplit(urljoin('https://resolver.invalid'+parsed.path,reference))
        return urlunsplit((parsed.scheme,parsed.netloc,joined.path,joined.query,joined.fragment))
    return urljoin(uri,reference)


class XmiError(ValueError): pass
class XmiReferenceError(XmiError): pass
class XmiUnsupportedError(XmiError): pass


@dataclass(frozen=True)
class Diagnostic:
    code: str
    uri: str
    element_id: str | None
    feature: str | None
    message: str
    severity: str = 'warning'


class XmiDocument:
    def __init__(self, uri, session):
        self.uri, self.session = uri, session
        self.roots, self.ids, self.diagnostics = [], {}, []
        self.resource_roots, self.opaque = {}, []
        self.runtime_values = []
        self.namespaces = {}
        self.aliases = {}

    @property
    def complete(self):
        return not any(d.code != 'documentation' for d in self.diagnostics)

    def resolve(self, reference, *, uri=None):
        target, fragment = urldefrag(_absolute(uri or self.uri, reference if '#' in reference else '#'+reference))
        target=self.aliases.get(target,target)
        try: return self.ids[target+'#'+fragment]
        except KeyError as error: raise XmiReferenceError('Unresolved reference: '+target+'#'+fragment) from error

    def validate(self):
        return [(root, root.validate(recursive=True)) for roots in self.resource_roots.values() for root in roots]


class _Reader:
    def __init__(self, uri, *, strict, resources, external_objects, profile_bindings, max_bytes, max_elements, max_depth, local_root=None):
        from . import ModelSession
        self.doc = XmiDocument(uri, ModelSession())
        self.strict, self.resources = strict, resources or {}
        self.external = external_objects or {}
        self.doc.ids.update(self.external)
        self.bindings = dict(profile_bindings or {})
        self.limits = max_bytes, max_elements, max_depth
        self.local_root = local_root
        self.trees, self.scopes, self.bases, self.nodes, self.runtime_nodes = {}, {}, {}, {}, []
        self.tasks, self.explicit, self.contexts = [], [], {}
        self.created, self.loaded_bytes, self.loaded_elements = [], 0, 0
        self.ignored_nodes=set()

    def problem(self, code, uri, node, feature, message, *, fatal=True):
        diagnostic = Diagnostic(code, uri, _meta(node, 'id'), feature, message, 'error' if fatal else 'warning')
        self.doc.diagnostics.append(diagnostic)
        if fatal and self.strict:
            cls = XmiReferenceError if code == 'reference' else XmiUnsupportedError if code == 'unsupported' else XmiError
            raise cls(f'{uri}#{diagnostic.element_id or ""} {feature or ""}: {message}')

    def opaque(self, uri, owner, node, code='extension'):
        self.ignored_nodes.update(node.iter())
        self.doc.opaque.append((owner, copy.deepcopy(node), dict(self.scopes.get(node, {}))))
        self.problem(code, uri, node, None, 'XML retained without interpreting its semantics', fatal=False)

    def parse(self, data, uri):
        if isinstance(data, str): data = data.encode('utf-8')
        self.loaded_bytes += len(data)
        if self.loaded_bytes > self.limits[0]: raise XmiError('Resource byte limit exceeded')
        declarations=re.sub(br'<!\[CDATA\[.*?\]\]>|<!--.*?-->',b'',data.replace(b'\x00',b''),flags=re.S)
        if re.search(br'<!\s*(?:DOCTYPE|ENTITY)\b', declarations, re.I): raise XmiError('DTD/entity declarations are not supported')
        stack, base_stack, pending, depth = [], [], [], 0
        try:
            parser = ET.iterparse(BytesIO(data), events=('start-ns','start','end'))
            for event, value in parser:
                if event == 'start-ns': pending.append(value)
                elif event == 'start':
                    depth += 1; self.loaded_elements += 1
                    if depth > self.limits[2] or self.loaded_elements > self.limits[1]: raise XmiError('XML depth/element limit exceeded')
                    scope = dict(stack[-1]) if stack else {}
                    scope.update(pending); pending.clear(); stack.append(scope)
                    self.scopes[value] = scope
                    base=_absolute(base_stack[-1] if base_stack else uri,value.get('{http://www.w3.org/XML/1998/namespace}base','')) if value.get('{http://www.w3.org/XML/1998/namespace}base') else (base_stack[-1] if base_stack else uri)
                    self.bases[value]=base; base_stack.append(base)
                    for prefix, namespace in scope.items(): self.doc.namespaces.setdefault(prefix, namespace)
                else: stack.pop(); base_stack.pop(); depth -= 1
            root = parser.root
        except ET.ParseError as error: raise XmiError('Invalid XML: '+str(error)) from error
        self.trees[uri] = root
        self.doc.resource_roots[uri] = []
        children = list(root) if _split(root.tag)[0] in XMI_NAMESPACES and _split(root.tag)[1] == 'XMI' else [root]
        for child in children:
            namespace, name = _split(child.tag)
            if namespace in XMI_NAMESPACES and name == 'Extension' and child.get('extender') == 'UmlLib':
                for metadata in child:
                    if metadata.tag == '{'+LIB_NS+'}profile': self.bindings[metadata.get('namespace')] = (uri, metadata.get('profile'))
                    elif metadata.tag == '{'+LIB_NS+'}context': self.contexts[uri+'#'+metadata.get('instance','')] = (uri, metadata.get('package'))
                    else: self.opaque(uri,None,metadata)
            elif namespace in XMI_NAMESPACES and name in ('Extension','Documentation'):
                self.opaque(uri,None,child,'documentation' if name=='Documentation' else 'extension')
            else: self.scan(child,uri)

    def class_name(self, node):
        type_ = _meta(node, 'type') or node.get('{'+XSI_NS+'}type')
        if type_:
            prefix, separator, name = type_.partition(':')
            return self.scopes[node].get(prefix if separator else '', ''), name if separator else prefix
        return _split(node.tag)

    def scan(self, node, uri, parent=None, feature=None):
        from . import UmlElement
        import Uml
        if _meta(node, 'idref') is not None or node.get('href') is not None: return
        namespace, name = self.class_name(node)
        if not namespace and parent is not None and feature is not None:
            spec = parent.properties()[feature]
            name, namespace = spec.type, UML_NS
        if namespace not in UML_NAMESPACES:
            if namespace and namespace not in XMI_NAMESPACES:
                self.runtime_nodes.append((node,uri,parent,feature))
                return
            self.problem('unsupported',uri,node,feature,'Expected a supported UML namespace and metaclass')
            self.opaque(uri,parent,node); return
        cls = Uml.Model.__registry__.get(name)
        if cls is None or not isinstance(cls,type) or not issubclass(cls,UmlElement):
            self.problem('unsupported',uri,node,feature,'Unknown UML metaclass: '+str(name)); self.opaque(uri,parent,node); return
        try: obj = cls()
        except TypeError as error:
            self.problem('type',uri,node,feature,str(error)); self.opaque(uri,parent,node); return
        self.created.append(obj); self.nodes[node] = obj
        identifier = _meta(node,'id')
        if identifier is not None and not re.fullmatch(r'[^\W\d][\w.-]*',identifier): raise XmiError('Invalid xmi:id: '+identifier)
        if identifier:
            key = uri+'#'+identifier
            if key in self.doc.ids: raise XmiError('Duplicate resource-local xmi:id: '+key)
            self.doc.ids[key] = obj
            obj._xmi_id, obj._xmi_uri = identifier, uri
        if _meta(node,'uuid'): obj._xmi_uuid=_meta(node,'uuid')
        if parent is None: self.doc.resource_roots[uri].append(obj)
        elif feature is not None: self.tasks.append((parent,feature,obj,uri,node))
        props = obj.properties()
        for key,value in node.attrib.items():
            ns, local = _split(key)
            if ns == 'http://www.w3.org/XML/1998/namespace' and local == 'base': continue
            if ns in XMI_NAMESPACES and local in ('id','type','uuid','version','nil') or ns == XSI_NS and local in ('type','schemaLocation','nil'): continue
            if ns or local not in props:
                self.problem('unsupported',uri,node,local,'Unknown UML attribute: '+key)
                self.opaque(uri,obj,ET.Element('attribute',{'name':key,'value':value})); continue
            self.tasks.append((obj,local,('attribute',value),uri,node))
        for child in node:
            ns,local = _split(child.tag)
            if ns in XMI_NAMESPACES and local == 'Extension' or not ns and local == 'eAnnotations':
                self.opaque(uri,obj,child); continue
            if ns or local not in props:
                self.problem('unsupported',uri,child,local,'Unknown UML child feature: '+child.tag); self.opaque(uri,obj,child); continue
            prop = props[local]
            from . import ENUMERATIONS
            if child.get('{'+XSI_NS+'}nil') == 'true' or _meta(child,'nil') == 'true':
                self.tasks.append((obj,local,None,uri,child))
            elif prop.type in ('Boolean','Integer','Real','String','UnlimitedNatural') or prop.type in ENUMERATIONS:
                self.tasks.append((obj,local,('text',child.text or ''),uri,child))
            elif _meta(child,'idref') is not None or child.get('href') is not None:
                self.tasks.append((obj,local,('reference',_meta(child,'idref') or child.get('href')),uri,child))
            else: self.scan(child,uri,obj,local)

    def ensure_resource(self, value, uri, node):
        absolute = _absolute(self.bases.get(node,uri) if '#' in value or node.get('href') else uri,value if '#' in value else '#'+value)
        resource,fragment = urldefrag(absolute)
        key = resource+'#'+fragment
        if key in self.external: return resource,fragment
        resource=self.doc.aliases.get(resource,resource)
        if resource not in self.trees:
            source = self.resources.get(resource, self.resources.get(value.split('#')[0]))
            if source is None and self.local_root is not None and urlparse(resource).scheme == 'file' and urlparse(resource).netloc in ('','localhost'):
                path = Path(unquote(urlparse(resource).path.lstrip('/') if __import__('os').name == 'nt' else urlparse(resource).path)).resolve()
                if path.is_relative_to(self.local_root) and path.is_file(): source = path
            if source is None:
                self.problem('reference',uri,node,None,'Resource is unavailable; provide resources/external_objects: '+resource)
                return resource,fragment
            if isinstance(source,Path):
                source=source.resolve(); canonical=source.as_uri()
                self.doc.aliases[resource]=canonical; resource=canonical
                if resource in self.trees: return resource,fragment
                if source.stat().st_size+self.loaded_bytes>self.limits[0]: raise XmiError('Resource byte limit exceeded')
                data=source.read_bytes()
            else: data=source
            self.parse(data,resource)
        return resource,fragment

    def reference(self, value, uri, node):
        from .semantics import _exchange_query_cache
        cache=_exchange_query_cache.get();token=_exchange_query_cache.set(None)
        count=len(self.tasks)
        try:
            resource,fragment=self.ensure_resource(value,uri,node)
            if cache is not None and len(self.tasks)!=count:
                cache.clear();self.assign_core()
        finally: _exchange_query_cache.reset(token)
        key=resource+'#'+fragment
        if key not in self.doc.ids:
            self.problem('reference',uri,node,None,'Unknown xmi:id: '+key); return None
        return self.doc.ids[key]

    def preload_runtime_resources(self):
        visited=set()
        while set(self.trees)-visited:
            uri=next(u for u in self.trees if u not in visited); visited.add(uri)
            for node in self.trees[uri].iter():
                if node in self.ignored_nodes: continue
                for key,value in node.attrib.items():
                    ns,name=_split(key)
                    if name=='href' or name.startswith('base_') or ns=='' and _split(node.tag)[0]==LIB_NS and name in ('profile','package'):
                        if '#' in value: self.ensure_resource(value,uri,node)

    def scalar(self, text, type_, registry):
        if type_ == 'String': return text
        if type_ == 'Boolean':
            if text not in ('true','false','1','0'): raise XmiError('Invalid Boolean: '+text)
            return text in ('true','1')
        if type_ == 'Integer':
            if not re.fullmatch(r'[+-]?[0-9]+',text.strip()): raise XmiError('Invalid Integer: '+text)
            return int(text)
        if type_ == 'Real': return float(text)
        if type_ == 'UnlimitedNatural':
            if text.strip()=='*': return float('inf')
            if not re.fullmatch(r'\+?[0-9]+',text.strip()): raise XmiError('Invalid UnlimitedNatural: '+text)
            return int(text)
        cls = registry.get(type_)
        if isinstance(cls,type) and issubclass(cls,Enum): return cls(text)
        raise XmiUnsupportedError('Unknown scalar type: '+str(type_))

    def value(self, raw, obj, feature, uri, node):
        prop = obj.properties()[feature]
        if not isinstance(raw,tuple): return [raw]
        form,text = raw
        if prop.type in ('Boolean','Integer','Real','String','UnlimitedNatural') or isinstance(obj.__registry__.get(prop.type),type) and issubclass(obj.__registry__[prop.type],Enum):
            many = prop.upper is None or prop.upper > 1
            tokens = text.split() if form=='attribute' and many and prop.type!='String' else [text]
            return [self.scalar(token,prop.type,obj.__registry__) for token in tokens]
        return [self.reference(token,uri,node) for token in (text.split() if form=='attribute' else [text])]

    def assign_core(self):
        from .specification import property_refines
        index = 0
        grouped = {}
        while index < len(self.tasks):
            obj,feature,raw,uri,node = self.tasks[index]; index += 1
            try: values = self.value(raw,obj,feature,uri,node)
            except (ValueError,TypeError) as error:
                if isinstance(error,XmiError) and self.strict: raise
                self.problem('value',uri,node,feature,str(error)); continue
            grouped.setdefault((obj,feature),(uri,node,[]))[2].extend(values)
        ordered = sorted(grouped.items(),key=lambda entry:(entry[0][0].properties()[entry[0][1]].flags.get('aggregation')!='composite',
                          sum(property_refines(q.id,entry[0][0].properties()[entry[0][1]].id) for q in entry[0][0].properties().values())))
        for (obj,feature),(uri,node,values) in ordered:
            prop = obj.properties()[feature]
            many = prop.upper is None or prop.upper>1
            if not many and values==[None]: values=[]
            if not many and len(values)>1:
                self.problem('multiplicity',uri,node,feature,'Multiple serialized values for a scalar feature'); continue
            if prop.flags.get('isUnique','true')=='true': values = list(dict.fromkeys(values))
            if prop.flags.get('isDerived')=='true' or prop.flags.get('isReadOnly')=='true':
                self.explicit.append((obj,feature,values,uri,node)); continue
            try: setattr(obj,feature,values if many else (values[0] if values else None))
            except (ValueError,TypeError,AttributeError,NotImplementedError) as error:
                self.problem('structure',uri,node,feature,str(error)); continue
            self.explicit.append((obj,feature,values,uri,node))
        for obj,feature,expected,uri,node in self.explicit:
            try: actual = obj._items(getattr(obj,feature))
            except (ValueError,TypeError,AttributeError,NotImplementedError) as error:
                self.problem('unsupported',uri,node,feature,'Cannot verify serialized feature: '+str(error)); continue
            prop = obj.properties()[feature]
            equal = actual==expected if prop.flags.get('isOrdered')=='true' or not (prop.upper is None or prop.upper>1) else set(actual)==set(expected)
            if not equal: self.problem('structure',uri,node,feature,'Explicit links conflict with ownership, opposites or subset/redefinition semantics')

    def runtime(self):
        from .native import kind
        from .profile_values import ProfileObject, containing_package
        from .stereotypes import StereotypeApplication
        # Bind serialized profile namespaces after core profile links are complete.
        for namespace,binding in list(self.bindings.items()):
            if isinstance(binding,tuple): self.bindings[namespace] = self.reference(binding[1],binding[0],self.trees[binding[0]])
        profiles = [o for o in self.created if kind(o,o,'Profile')]
        for profile in profiles:
            if profile.URI: self.bindings.setdefault(profile.URI,profile)
        for alias,canonical in self.doc.aliases.items():
            candidates=[o for o in self.doc.resource_roots.get(canonical,()) if kind(o,o,'Profile')]
            if len(candidates)==1: self.bindings.setdefault(alias,candidates[0])
        for namespace,source in self.resources.items():
            if isinstance(source,Path):
                candidates=[o for o in self.doc.resource_roots.get(source.resolve().as_uri(),()) if kind(o,o,'Profile')]
                if len(candidates)==1: self.bindings.setdefault(namespace,candidates[0])
        for namespace,profile in self.bindings.items():
            if profile in self.created and not profile.URI: profile._xmi_namespace=namespace
        staged = []
        runtime_types={}
        runtime_seen={entry[0] for entry in self.runtime_nodes}
        for node,uri,parent,feature in self.runtime_nodes:
            namespace,name = runtime_types.get(node,self.class_name(node))
            profile = self.bindings.get(namespace)
            if profile is None:
                self.problem('unsupported',uri,node,feature,'Unknown profile namespace: '+namespace); self.opaque(uri,parent,node); continue
            candidates = [o for o in profile.allOwnedElements() if kind(o,o,'Classifier') and o.name == name]
            if len(candidates)!=1:
                self.problem('unsupported',uri,node,feature,'Profile type name must identify one classifier: '+name); self.opaque(uri,parent,node); continue
            classifier = candidates[0]
            identifier = _meta(node,'id')
            if identifier is not None and not re.fullmatch(r'[^\W\d][\w.-]*',identifier): raise XmiError('Invalid xmi:id: '+identifier)
            context = self.contexts.get(uri+'#'+str(identifier))
            package = self.reference(context[1],context[0],node) if context else None
            if package is None and isinstance(parent,ET.Element) and parent in self.nodes: package=self.nodes[parent].package
            if kind(classifier,classifier,'Stereotype'):
                from .native.constraints_remaining import base_properties
                bases = [p for p in base_properties(classifier) if p.name in node.attrib]
                if len(bases)!=1: self.problem('structure',uri,node,None,'Stereotype application needs exactly one populated base property'); continue
                base = self.reference(node.get(bases[0].name),uri,node)
                if base is None: continue
                value = StereotypeApplication(classifier,base,base_property=bases[0])
                package = containing_package(base)
            else:
                if package is None:
                    packages = [o for o in self.doc.resource_roots[uri] if kind(o,o,'Package') and not kind(o,o,'Profile')]
                    if len(packages)==1: package = packages[0]
                if package is None: self.problem('structure',uri,node,None,'Profile instance requires an unambiguous package context'); continue
                value = ProfileObject(classifier,package)
            self.nodes[node] = value; self.doc.runtime_values.append(value)
            if identifier:
                key=uri+'#'+identifier
                if key in self.doc.ids: raise XmiError('Duplicate resource-local xmi:id: '+key)
                self.doc.ids[key]=value
                value._xmi_id,value._xmi_uri=identifier,uri
            staged.append((node,uri,value,classifier))
            for child in node:
                if child in runtime_seen or _meta(child,'idref') or child.get('href'): continue
                matching=[p for p in value._properties() if p.name==child.tag]
                if len(matching)==1 and matching[0].type is not None and (kind(classifier,matching[0].type,'Class') or kind(classifier,matching[0].type,'DataType')) and not any(kind(classifier,matching[0].type,n) for n in ('PrimitiveType','Enumeration')):
                    child_namespace,child_name=self.class_name(child)
                    if child_namespace in UML_NAMESPACES: raise XmiUnsupportedError('Inline UML elements in runtime tags require separate definitions')
                    if not child_namespace: runtime_types[child]=(namespace,matching[0].type.name)
                    self.runtime_nodes.append((child,uri,node,child.tag));runtime_seen.add(child)
        runtime_explicit=[]
        for node,uri,value,classifier in staged:
            props = value._properties(); names = {p.name:p for p in props}
            fields={}
            from .native.constraints_remaining import base_properties
            bases = {p.name for p in base_properties(classifier)} if kind(classifier,classifier,'Stereotype') else set()
            for key,text in node.attrib.items():
                ns,name = _split(key)
                if ns in XMI_NAMESPACES or name in bases: continue
                if ns or name not in names: self.problem('unsupported',uri,node,name,'Unknown runtime profile attribute'); continue
                fields.setdefault(name,[]).append(('attribute',text))
            for child in node:
                ns,name=_split(child.tag)
                if ns or name not in names: self.problem('unsupported',uri,child,name,'Unknown runtime profile child'); self.opaque(uri,value,child); continue
                if child in self.nodes: fields.setdefault(name,[]).append(('object',self.nodes[child]))
                elif child.get('{'+LIB_NS+'}empty')=='true': fields.setdefault(name,[]).append(('empty',None))
                elif child.get('{'+XSI_NS+'}nil')=='true' or _meta(child,'nil')=='true': fields.setdefault(name,[]).append(('null',None))
                else: fields.setdefault(name,[]).append(('reference',_meta(child,'idref') or child.get('href')) if _meta(child,'idref') or child.get('href') else ('text',child.text or ''))
            values={}
            for name,encoded in fields.items():
                prop=names[name]; result=[]
                try:
                    for form,text in encoded:
                        if form=='empty': continue
                        if form=='null': result.append(None); continue
                        if form=='object': result.append(text); continue
                        if kind(classifier,prop.type,'PrimitiveType'):
                            result.extend(self.scalar(t,prop.type.name,classifier.__registry__) for t in (text.split() if form=='attribute' and prop.upperBound()>1 and prop.type.name!='String' else [text]))
                        elif kind(classifier,prop.type,'Enumeration'): result.extend(text.split() if form=='attribute' and prop.upperBound()>1 else [text])
                        else: result.extend(self.reference(t,uri,node) for t in (text.split() if form=='attribute' else [text]))
                    if prop.upperBound()<=1 and len(result)>1: raise XmiError('Multiple runtime scalar values: '+name)
                    raw=result if prop.upperBound()>1 else (result[0] if result else None)
                    value._normalize(prop,raw,check_lower=False)
                    values[prop]=raw
                except (ValueError,TypeError,NotImplementedError) as error:
                    self.problem('unsupported' if isinstance(error,NotImplementedError) or isinstance(error,XmiUnsupportedError) else 'value',uri,node,name,str(error))
                    if name in node.attrib: self.opaque(uri,value,ET.Element('attribute',{'name':name,'value':node.get(name)}))
                    for child in node:
                        if child.tag==name: self.opaque(uri,value,child)
            try:
                staged_values=dict(value._values)
                for prop,raw in values.items():
                    if prop.isDerived: raise XmiUnsupportedError('Derived runtime tag requires an evaluator')
                    staged_values[prop]=value._normalize(prop,raw,check_lower=False)
                value._commit(staged_values)
                runtime_explicit.extend((value,prop,staged_values[prop],uri,node) for prop in values)
            except (ValueError,TypeError,NotImplementedError) as error: self.problem('structure',uri,node,None,str(error))
        for value,prop,expected,uri,node in runtime_explicit:
            actual=value._values.get(prop,())
            equal=actual==expected if prop.isOrdered or prop.upperBound()<=1 else set(actual)==set(expected)
            if not equal:
                self.problem('structure',uri,node,prop.name,'Explicit runtime association ends conflict')

    def run(self,data):
        from . import UmlElement,_mutation
        from .model_session import current_session
        from .profile_values import _records
        if _mutation.get() is not None: raise XmiError('Import cannot run during a model mutation')
        original_records=set(_records)
        runtime_state={r:(dict(r._values),r._composite_owner,r._package,r._registry_package,getattr(r,'_element',None),getattr(r,'_base_property',None)) for r in original_records}
        models=list(UmlElement.__instances__)
        maps={o:dict(getattr(o,'_stereotype_applications',{})) for o in models}
        registries={o:set(getattr(o,'_profile_instances',())) for o in models}
        transaction={'snapshots':{},'active':set()}
        mutation_token=_mutation.set(transaction); session_token=current_session.set(self.doc.session)
        try:
            self.parse(data,self.doc.uri); self.preload_runtime_resources(); self.assign_core()
            from .semantics import _exchange_query_cache
            query_token=_exchange_query_cache.set({})
            try: self.runtime()
            finally: _exchange_query_cache.reset(query_token)
            self.doc.roots=list(self.doc.resource_roots[self.doc.uri])
            return self.doc
        except Exception:
            UmlElement._rollback(transaction)
            for record in set(_records)-original_records:
                _records.discard(record); record._deleted=True
                if record._registry_package is not None: getattr(record._registry_package,'_profile_instances',set()).discard(record)
            for record,state in runtime_state.items():
                record._values,record._composite_owner,record._package,record._registry_package,base,prop=state
                if hasattr(record,'_element'): record._element,record._base_property=base,prop
            for obj,mapping in maps.items(): obj._stereotype_applications=mapping
            for obj,registry in registries.items(): obj._profile_instances=registry
            for obj in self.created:
                obj.__instances__.discard(obj); self.doc.session.elements.discard(obj); obj._deleted=True
            raise
        finally: current_session.reset(session_token); _mutation.reset(mutation_token)


def loads(data, *, uri='memory:/model.xmi', strict=True, resources=None, external_objects=None, profile_bindings=None,
          max_bytes=64*1024*1024,max_elements=500000,max_depth=256):
    """Import XML bytes/text. External HTTP/pathmap resources require explicit maps."""
    return _Reader(uri,strict=strict,resources=resources,external_objects=external_objects,profile_bindings=profile_bindings,
                   max_bytes=max_bytes,max_elements=max_elements,max_depth=max_depth).run(data)


def load(path, *, strict=True,resources=None,external_objects=None,profile_bindings=None,
         max_bytes=64*1024*1024,max_elements=500000,max_depth=256):
    """Import a file and relative sibling resources within its directory, offline."""
    path=Path(path).resolve()
    if path.stat().st_size>max_bytes: raise XmiError('Resource byte limit exceeded')
    reader=_Reader(path.as_uri(),strict=strict,resources=resources,external_objects=external_objects,profile_bindings=profile_bindings,
                   max_bytes=max_bytes,max_elements=max_elements,max_depth=max_depth,local_root=path.parent)
    return reader.run(path.read_bytes())


def dumps(model, *, bundle=True, external_references=None):
    """Serialize a model/document. Bundling closes stored references and ownership.

    With bundle=False external targets require URI#id mappings or imported identities.
    UmlLib profile namespace/context metadata is an explicit XMI extension.
    """
    from .semantics import _exchange_query_cache
    token=_exchange_query_cache.set({})
    try: return _dumps(model,bundle=bundle,external_references=external_references)
    finally: _exchange_query_cache.reset(token)


def _dumps(model, *, bundle=True, external_references=None):
    from . import UmlElement
    from .native import kind
    from .specification import property_redefines,property_refines
    from .profile_values import ProfileObject,EnumValue
    from .stereotypes import StereotypeApplication,applications
    document=model if isinstance(model,XmiDocument) else None
    roots=list(document.roots) if document else [model] if isinstance(model,UmlElement) else list(model)
    references=external_references or {}
    if not roots or any(not isinstance(r,UmlElement) for r in roots): raise XmiError('Expected one or more UML roots')
    objects,records,seen,pending=[],[],set(),list(reversed(roots))
    def properties(obj):
        props=obj.properties()
        return [(name,p) for name,p in props.items() if p.flags.get('isDerived')!='true'
                and not any(q.id!=p.id and q.flags.get('isDerived')!='true' and property_redefines(q.id,p.id) for q in props.values())]
    while pending:
        obj=pending.pop()
        if obj in seen: continue
        obj._ensure_alive(); seen.add(obj); objects.append(obj)
        for name,prop in properties(obj):
            for target in obj._items(getattr(obj,name)):
                if isinstance(target,UmlElement) and (prop.flags.get('aggregation')=='composite' or bundle): pending.append(target)
        if bundle and obj._container is not None: pending.append(obj._container)
        candidates=list(applications(obj))+list(getattr(obj,'_profile_instances',()))
        for record in candidates:
            if record in records or record.is_deleted: continue
            records.append(record)
        # Profile record references can introduce additional UML/profile objects.
        record_index=0
        while record_index<len(records):
            record=records[record_index]; record_index+=1
            record._ensure_alive()
            for target in (record.classifier,record.package,getattr(record,'element',None)):
                if target is not None and bundle and target not in seen: pending.append(target)
            for values in record._values.values():
                for target in values:
                    if isinstance(target,ProfileObject) and target not in records: records.append(target)
                    elif isinstance(target,UmlElement) and bundle and target not in seen: pending.append(target)
                    elif isinstance(target,EnumValue) and bundle and target.literal not in seen: pending.append(target.literal)
    identities,used={},set()
    for obj in objects+records:
        candidate=getattr(obj,'_xmi_id',None) or 'id'+str(len(identities)+1)
        if not re.fullmatch(r'[^\W\d][\w.-]*',candidate): candidate='id'+str(len(identities)+1)
        identifier=candidate; suffix=1
        while identifier in used: suffix+=1; identifier=candidate+'_'+str(suffix)
        identities[obj]=identifier; used.add(identifier)
    def reference(obj):
        if obj in identities: return identities[obj]
        target=references.get(obj)
        if target is None and getattr(obj,'_xmi_uri',None) and getattr(obj,'_xmi_id',None): target=obj._xmi_uri+'#'+obj._xmi_id
        if target is None or '#' not in target: raise XmiReferenceError('External target needs URI#id: '+obj.__spec__.name)
        return target
    namespaces={'xmi':XMI_NS,'uml':UML_NS,'lib':LIB_NS,'xsi':XSI_NS}
    def prefix(namespace):
        if namespace=='http://www.w3.org/XML/1998/namespace': return 'xml'
        for p,n in namespaces.items():
            if n==namespace: return p
        p='p'+str(len(namespaces)); namespaces[p]=namespace; return p
    profile_namespaces={}
    for record in records:
        profile=record._profile
        if profile is None: raise XmiError('Runtime classifier is no longer in a Profile')
        namespace=profile.URI or getattr(profile,'_xmi_namespace',None) or 'urn:umllib:profile:'+reference(profile)
        profile_namespaces[profile]=namespace; prefix(namespace)
    root=ET.Element('xmi:XMI',{'xmi:version':'2.5.1'})
    containers={}
    for obj in objects:
        for name,prop in properties(obj):
            if prop.flags.get('aggregation')!='composite': continue
            for child in obj._items(getattr(obj,name)):
                if not isinstance(child,UmlElement): continue
                previous=containers.get(child)
                if previous is None or property_refines(prop.id,previous[2].id): containers[child]=(obj,name,prop)
    emitted=set()
    def text(value):
        if isinstance(value,Enum): return value.value
        if isinstance(value,EnumValue): return value.name
        if type(value) is bool: return 'true' if value else 'false'
        if type(value) is float and value==float('inf'): return '*'
        return str(value)
    def emit(obj,parent,feature=None,depth=0):
        if depth>256: raise XmiError('Export containment depth exceeds 256')
        if obj in emitted: raise XmiError('Multiple serialized composite owners')
        emitted.add(obj)
        node=ET.SubElement(parent,feature or 'uml:'+obj.__spec__.name,{'xmi:id':identities[obj]})
        if getattr(obj,'_xmi_uuid',None): node.set('xmi:uuid',obj._xmi_uuid)
        if feature: node.set('xmi:type','uml:'+obj.__spec__.name)
        for name,prop in properties(obj):
            value=getattr(obj,name); many=prop.upper is None or prop.upper>1
            if value is None and prop.default is not None:
                ET.SubElement(node,name,{'xsi:nil':'true'})
            for item in obj._items(value):
                if isinstance(item,UmlElement):
                    container=containers.get(item)
                    if item in identities and container is not None and container[:2]==(obj,name): emit(item,node,name,depth+1)
                    else:
                        ref=reference(item)
                        ET.SubElement(node,name,{'href':ref} if '#' in ref else {'xmi:idref':ref})
                elif many: ET.SubElement(node,name).text=text(item)
                else: node.set(name,text(item))
        return node
    for obj in objects:
        if obj not in containers: emit(obj,root)
    for obj in objects:
        if obj not in emitted: raise XmiError('Containment graph has no serializable root')
    metadata=None
    if records:
        metadata=ET.SubElement(root,'xmi:Extension',{'extender':'UmlLib'})
        for profile,namespace in profile_namespaces.items(): ET.SubElement(metadata,'lib:profile',{'namespace':namespace,'profile':reference(profile)})
    for record in sorted(records,key=lambda r:identities[r]):
        classifier=record.classifier
        matches=[o for o in record._profile.allOwnedElements() if kind(o,o,'Classifier') and o.name==classifier.name]
        if len(matches)!=1 or not classifier.name or not re.fullmatch(r'[^\W\d][\w.-]*',classifier.name): raise XmiUnsupportedError('Profile classifier must have one unambiguous XML-compatible name')
        node=ET.SubElement(root,prefix(profile_namespaces[record._profile])+':'+classifier.name,{'xmi:id':identities[record]})
        if isinstance(record,StereotypeApplication):
            if record.element is None: raise XmiError('Detached stereotype application cannot be exported')
            node.set(record._base_property.name,reference(record.element))
        else: ET.SubElement(metadata,'lib:context',{'instance':identities[record],'package':reference(record.package)})
        for prop,values in record._values.items():
            if prop not in record._properties(): raise XmiError('Obsolete runtime tag cannot be exported')
            if not prop.name or not re.fullmatch(r'[^\W\d][\w.-]*',prop.name): raise XmiUnsupportedError('Tag name must be XML-compatible')
            if not values:
                ET.SubElement(node,prop.name,{'lib:empty':'true'} if prop.upperBound()>1 else {'xsi:nil':'true'})
            for value in values:
                if isinstance(value,(UmlElement,ProfileObject)):
                    ref=reference(value); ET.SubElement(node,prop.name,{'href':ref} if '#' in ref else {'xmi:idref':ref})
                elif prop.upperBound()>1: ET.SubElement(node,prop.name).text=text(value)
                else: node.set(prop.name,text(value))
    ET.indent(root)
    if document:
        def convert(node,scope):
            cloned=ET.Element(node.tag,dict(node.attrib)); cloned.text,cloned.tail=node.text,node.tail
            for key in [cloned.tag]+list(cloned.attrib):
                ns,name=_split(key)
                if ns:
                    p=prefix(ns)
                    if p in scope and scope[p]!=ns:
                        p='o'+str(len(namespaces))
                        while p in scope or p in namespaces: p+='x'
                        namespaces[p]=ns
                    converted=p+':'+name
                    if key==cloned.tag: cloned.tag=converted
                    else: cloned.set(converted,cloned.attrib.pop(key))
            for child in node: cloned.append(convert(child,scope))
            # QName-valued vendor attributes retain their local prefix bindings.
            for p,ns in scope.items(): cloned.set('xmlns'+(':'+p if p else ''),ns)
            return cloned
        by_id={node.get('xmi:id'):node for node in root.iter() if node.get('xmi:id')}
        for owner,node,scope in document.opaque:
            if owner is None: root.append(convert(node,scope))
            elif owner in identities:
                target=by_id[identities[owner]]
                if node.tag=='attribute':
                    ns,name=_split(node.get('name')); target.set(prefix(ns)+':'+name if ns else name,node.get('value'))
                else: target.append(convert(node,scope))
    for p,namespace in namespaces.items(): root.set('xmlns:'+p,namespace)
    return ET.tostring(root,encoding='unicode',xml_declaration=True)


def dump(model,path,**options):
    """Write UTF-8 XML after successful graph serialization."""
    data=dumps(model,**options)
    Path(path).write_text(data,encoding='utf-8')
