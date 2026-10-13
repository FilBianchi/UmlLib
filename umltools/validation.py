"""Structured, located validation without changing the legacy tuple API."""
from dataclasses import dataclass
from functools import lru_cache
from importlib.resources import files
import json


@lru_cache(maxsize=1)
def _obligations():
    return json.loads(files('umltools').joinpath('data/validation-obligations.json').read_text(encoding='utf-8'))


@dataclass(frozen=True)
class ValidationIssue:
    element: object
    category: str
    rule: str
    status: str
    severity: str
    message: str
    uri: str | None = None
    element_id: str | None = None
    feature: str | None = None
    path: str | None = None
    cause: str | None = None

    def to_dict(self):
        return {key: getattr(self, key) for key in ('category','rule','status','severity','message','uri','element_id','feature','path','cause')}


@dataclass(frozen=True)
class ValidationReport:
    issues: tuple
    checked_elements: int
    semantic_version: str
    complete_import: bool = True

    @property
    def violations(self): return tuple(i for i in self.issues if i.status == 'violation')
    @property
    def unsupported(self): return tuple(i for i in self.issues if i.status == 'unsupported')
    @property
    def evaluation_errors(self): return tuple(i for i in self.issues if i.status == 'evaluation_error')
    @property
    def warnings(self): return tuple(i for i in self.issues if i.status == 'incomplete')
    @property
    def complete(self):
        return self.complete_import and not (self.unsupported or self.evaluation_errors or self.warnings)
    @property
    def is_valid(self):
        return False if self.violations else True if self.complete else None

    def to_dict(self):
        return {'semantic_version':self.semantic_version,'checked_elements':self.checked_elements,
                'complete_import':self.complete_import,'complete':self.complete,'is_valid':self.is_valid,
                'issues':[i.to_dict() for i in self.issues]}


def _issue(element, category, rule, identities, cause=None):
    if category.startswith('unsupported'):
        status, severity, message = 'unsupported', 'warning', 'This semantic obligation could not be evaluated.'
    elif category == 'cross session reference':
        status, severity, message = 'incomplete', 'warning', 'Reference crosses model extents; reverse-query context may be incomplete.'
    elif category.startswith('invalid ') or category == 'evaluation error':
        status, severity, message = 'evaluation_error', 'error', 'Evaluation failed or required model context is incomplete.'
    else:
        status, severity, message = 'violation', 'error', 'The implemented requirement is not satisfied.'
    feature = None
    if hasattr(type(element), '__spec__'):
        for name, prop in element.properties().items():
            if prop.id == rule:
                feature = name
                if category == 'multiplicity': message = f'{name} requires {prop.lower}..{prop.upper if prop.upper is not None else "*"} values.'
                break
    key = identities.get(id(element))
    if key:
        uri, identifier = key.rsplit('#',1)
    else:
        uri, identifier = getattr(element,'_xmi_uri',None), getattr(element,'_xmi_id',None)
    try:
        path = element.qualifiedName if hasattr(type(element), '__spec__') and 'qualifiedName' in element.properties() else None
    except Exception:
        path = None
    return ValidationIssue(element,category,rule,status,severity,message,uri,identifier,feature,path,cause)


def _report(elements, version, *, identities=None, complete_import=True):
    seen, issues = set(), []
    for element in elements:
        if id(element) in seen or element.is_deleted: continue
        seen.add(id(element))
        causes = {}
        try:
            results = element.validate(_causes=causes) if hasattr(type(element),'__spec__') else element.validate()
        except Exception as error:
            results = [('evaluation error', f'{type(error).__name__}: {error}')]
        issues.extend(_issue(element,category,rule,identities or {},causes.get((category,rule))) for category,rule in results)
        # These are declared coverage gaps, not failed model predicates. The
        # census is conservative by metaclass, and is not a complete prose audit.
        if version == '2.5.1' and hasattr(type(element),'__spec__'):
            kinds={base.__dict__['__spec__'].name for base in type(element).__mro__ if '__spec__' in base.__dict__}
            reported={rule for category,rule in results if category.startswith('unsupported')}
            for obligation in _obligations()['requirements']:
                if obligation['owner'] in kinds and obligation['rule'] not in reported:
                    issue=_issue(element,'unsupported requirement',obligation['rule'],identities or {},obligation['limitation'])
                    issues.append(issue)
    return ValidationReport(tuple(issues),len(seen),version,complete_import)


def validate_element(element, *, recursive=False):
    element._ensure_alive()
    elements, pending, seen = [], [element], set()
    while pending:
        current = pending.pop()
        if id(current) in seen: continue
        seen.add(id(current));elements.append(current)
        if recursive: pending.extend(current.ownedElement)
    return _report(elements, element.semantic_version)


def validate_document(document):
    identities = {}
    for key,obj in document.ids.items(): identities.setdefault(id(obj),key)
    elements = sorted(document.session.elements, key=lambda e: identities.get(id(e),'')) + list(document.runtime_values)
    return _report(elements,document.semantic_version,identities=identities,complete_import=document.complete)
