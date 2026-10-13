"""UML 2.4.1 model exchange, using the isolated 2.4.1 backend."""
from ._runtime import engine
load=engine.xmi.load
loads=engine.xmi.loads
dump=engine.xmi.dump
dumps=engine.xmi.dumps
XmiDocument=engine.xmi.XmiDocument
XmiError=engine.xmi.XmiError
XmiReferenceError=engine.xmi.XmiReferenceError
XmiUnsupportedError=engine.xmi.XmiUnsupportedError
XmiVersionError=engine.xmi.XmiVersionError
Diagnostic=engine.xmi.Diagnostic
detect_version=engine.xmi.detect_version
XMI_NS=engine.xmi.XMI_NS
UML_NS=engine.xmi.UML_NS
