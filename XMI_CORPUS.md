# Public XMI corpus verification

Sources are pinned by commit and SHA-256 in `scripts/xmi-corpus.json`. Original files are fetched into an ignored cache rather than redistributed in this repository.

The counts below include dependency resources (libraries, metamodels and profiles), not only the entry file. Spring cases use strict decoding. Eclipse cases use permissive decoding: decoded graph counts and normalized known-feature graphs round-trip, while opaque extensions/unsupported profile values remain explicit gaps. This is not a UML/XMI conformity certificate.

| Entry file | UML objects | Runtime profile values | Diagnostics | Decoding |
| --- | ---: | ---: | ---: | --- |
| [simple-machine.uml](https://raw.githubusercontent.com/spring-attic/spring-statemachine/b78817dd691c70760fa428db5ae1bb133ea73380/docs/src/reference/asciidoc/samples/simple-machine.uml) | 11 | 0 | 0 | strict |
| [simple-submachine.uml](https://raw.githubusercontent.com/spring-attic/spring-statemachine/b78817dd691c70760fa428db5ae1bb133ea73380/spring-statemachine-uml/src/test/resources/org/springframework/statemachine/uml/simple-submachine.uml) | 20 | 0 | 0 | strict |
| [ordershipping.uml](https://raw.githubusercontent.com/spring-attic/spring-statemachine/b78817dd691c70760fa428db5ae1bb133ea73380/spring-statemachine-samples/ordershipping/src/main/resources/ordershipping.uml) | 83 | 0 | 0 | strict |
| [multijoin-forkjoin.uml](https://raw.githubusercontent.com/spring-attic/spring-statemachine/b78817dd691c70760fa428db5ae1bb133ea73380/spring-statemachine-uml/src/test/resources/org/springframework/statemachine/uml/multijoin-forkjoin.uml) | 43 | 0 | 0 | strict |
| [linked-regions.uml](https://raw.githubusercontent.com/spring-attic/spring-statemachine/b78817dd691c70760fa428db5ae1bb133ea73380/spring-statemachine-build-tests/src/test/resources/org/springframework/statemachine/buildtests/linked-regions.uml) | 76 | 0 | 0 | strict |
| [Bug497359.uml](https://raw.githubusercontent.com/eclipse-uml2/uml2/94fcae32ce92207a4930b75dbc847b2c88d5d775/tests/org.eclipse.uml2.uml.tests/src/org/eclipse/uml2/uml/bug/tests/Bug497359.uml) | 9124 | 861 | 55 | permissive |
| [UML.metamodel.uml](https://raw.githubusercontent.com/eclipse-uml2/uml2/94fcae32ce92207a4930b75dbc847b2c88d5d775/plugins/org.eclipse.uml2.uml.resources/metamodels/UML.metamodel.uml) | 8723 | 461 | 54 | permissive |

Checks: SHA-256 integrity, decoding, export/reimport metaclass and runtime-instance counts, and stability of the normalized known graph on another export/reimport. Independent unit cases additionally assert specific link identities, composite ownership, subset/redefined ends, profile values and failed-import rollback. Counts and normalization alone do not prove every source feature was interpreted.

For Eclipse, diagnostics include retained EMF annotations and unknown extension content. Model-defined primitives such as EString are handled through generic typed lexical values, without Eclipse-specific name aliases. Their semantic validation requires explicit per-definition codecs. Opaque vendor reference encodings are not rewritten when resources are bundled. The full diagnostic report is `.build-tmp/xmi-corpus/report.json` and is uploaded by the Public XMI corpus workflow.

Reproduce:

```console
python -m scripts.verify_xmi_corpus --fetch --complex
```

Without `--fetch`, the verifier requires an existing cache and checks all hashes. Without `--complex`, it verifies the five strict Spring entry files. The Showcase file is pinned for future profile-adapter work; its Papyrus ActionLanguage profile dependency is not in the current decoded suite.

The current UML XMI implementation supports represented core/profile graph exchange and model-defined primitive lexical values. CMOF, EMF positional/name fragments, XPointer, general expression adapters and vendor diagram semantics remain open.

Since 0.18.0, the five strict Spring cases also pass using the explicit native
2.4.1 backend with the same object counts, zero diagnostics, reference identity
and stable known-graph export/reimport. Their Eclipse namespace is not proof of
the producer's exact UML release. Reproduce with
`python -m scripts.verify_xmi_corpus --fetch --semantic-version 2.4.1`;
the report is `report-2.4.1.json` in the same cache. The workflow uploads both reports.
The complex runtime-profile corpus remains a 2.5.1 check; profiles are retained
opaque by the 2.4.1 reader. A pinned original OMG PrimitiveTypes fixture is tested
offline in `tests/fixtures/xmi241`, including its four unimplemented MOF extension tags.
