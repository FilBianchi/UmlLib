"""Independent UML 2.4.1 state using the shared structural engine."""
from umltools.version_backend import backend_241

engine=backend_241()
UmlElement=engine.UmlElement
SPECIFICATIONS=engine.SPECIFICATIONS
UnsupportedSemanticsError=engine.UnsupportedSemanticsError
NativeNotImplemented=engine.NativeNotImplemented
operation=engine.operation
