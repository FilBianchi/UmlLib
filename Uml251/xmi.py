"""UML 2.5.1 exchange API."""
from umltools import xmi as _exchange
from umltools.xmi import XmiDocument,XmiError,XmiReferenceError,XmiUnsupportedError,XmiVersionError,Diagnostic,detect_version,XMI_NS,UML_NS


def _version(options,key):
    if options.get(key) not in (None,'2.5.1'):
        raise XmiUnsupportedError('Uml251.xmi only exchanges UML 2.5.1')
    options[key]='2.5.1'
    return options


def loads(data,**options):return _exchange.loads(data,**_version(options,'semantic_version'))
def load(path,**options):return _exchange.load(path,**_version(options,'semantic_version'))
def dumps(model,**options):return _exchange.dumps(model,**_version(options,'target_version'))
def dump(model,path,**options):return _exchange.dump(model,path,**_version(options,'target_version'))
