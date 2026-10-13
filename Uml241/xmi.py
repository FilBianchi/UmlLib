"""UML 2.4.1 exchange entry points; currently raise an explicit unsupported error."""
from ._runtime import engine
load=engine.xmi.load
loads=engine.xmi.loads
dump=engine.xmi.dump
dumps=engine.xmi.dumps
