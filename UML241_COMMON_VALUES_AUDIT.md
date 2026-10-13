# Audit UML 2.4.1: CommonStructure e Values

L'audit riguarda le dichiarazioni dei gruppi API CommonStructure e Values, incluse
MultiplicityElement e le query di Package necessarie agli import. I gruppi sono
facade organizzative: la fonte normativa merged 2.4.1 resta piatta.
Fonte: `umltools/data/UML-2.4.1.xmi`, documento elencato dalla
[pagina OMG UML 2.4.1](https://www.omg.org/spec/UML/2.4.1).

Sono registrate **63 operazioni, 30 vincoli e 16 derivazioni** in questo ambito:
due derivazioni native, sette tramite query, quattro union e tre intrinseche
strutturali. Complessivamente il backend 2.4.1 ha 64 operazioni native abilitate
(include anche ExtensionEnd.lowerBound). Inventario delle dichiarazioni, condizioni
e riferimenti sorgente in [uml241-common-values-audit.json](uml241-common-values-audit.json).

```console
python -m scripts.report_uml241_audit
```

Questi conteggi indicano implementazioni collegate alle dichiarazioni, non una
certificazione di tutte le combinazioni del modello. Override e dipendenze di
Classification non ancora verificati restano unsupported: per esempio il member
di un Classifier richiede inheritedMember, e la compatibilità di ValueSpecification
tipizzate richiede la conformità dei loro classifier.

## Comportamenti verificati

- Nomi qualificati, catena dei namespace, package proprietari, rinomina e nomi assenti.
- ElementImport: alias, nome originale, visibilità; Namespace: collisioni tra import,
  shadowing da membri locali, nomi degli import e distinguibilità.
- Package: import privati accessibili internamente senza riesportazione, import
  pubblici transitivi, membri visibili e query strutturali di package/type/stereotype.
- TemplateableElement/ParameterableElement: query base, direzione della compatibilità,
  formal/default, appartenenza e unicità delle sostituzioni e proprietà degli elementi.
- Molteplicità: inclusione di cardinalità/intervalli, compatibilità, uguaglianza,
  infinito, precondizioni dei limiti e limiti esplicitamente non calcolabili.
- Constraint: risultato Boolean (anche false), mancata autoapplicazione e assenza
  di effetti collaterali; per espressioni esterne servono fatti espliciti di un analyser.
- StringExpression: concatenazione, tipi degli operand e esclusività delle alternative.
- OpaqueExpression: corpo/linguaggio, solo parametri di ritorno, singolo risultato,
  selezione del parametro return e precondizioni delle query numeriche.
- DurationConstraint/DurationObservation: corrispondenza della molteplicità firstEvent.

## Differenze mantenute rispetto a UML 2.5.1

| Dichiarazione | Implementazione 2.4.1 |
| --- | --- |
| NamedElement.allNamespaces | Segue namespace verso l'esterno; non aggiunge il contesto del template introdotto dalla formula 2.5.1 |
| NamedElement.visibility_needs_ownership | Namespace assente implica visibilità assente, anche su un elemento radice |
| ParameterableElement.isCompatibleWith | Verifica se il parametro p è un'istanza del tipo dinamico di self, nell'ordine della formula 2.4.1 |
| ValueSpecification.isCompatibleWith | Usa lo stesso ordine e richiede conformità dei tipi; un override di Classification ancora unsupported non è sostituito con false/true |
| OpaqueExpression.only_return_result_parameters | Consente solo return; la versione 2.5.1 consente anche in non-stream |
| MultiplicityElement.lowerBound/upperBound | Default 1 solo se l'espressione manca; una ValueSpecification presente che restituisce undefined produce None |
| Vincoli di molteplicità | Le implicazioni lower_ge_0/upper_ge_lower sono vere quando il loro antecedente richiede limiti che sono undefined; le query con precondizioni invece rifiutano quei limiti |

`isMultivalued` richiede soltanto upperBound definito. `includesCardinality` e
`includesMultiplicity` richiedono i limiti dichiarati dalle loro precondizioni.
Per intervalli validi, compatibleWith equivale all'inclusione dell'intervallo di self
in quello di other; un intervallo vuoto soddisfa la quantificazione universalmente
per vacuità, senza rendere valido il modello che viola upper_ge_lower.

## Interpretazioni esplicite dei refusi e dei segnaposto

Le formule sono lette come riferimento, mai eseguite. Le ownedComment normative
sono state lette insieme ai corpi e alle firme. Sono applicate queste interpretazioni:

| Fonte | Decisione |
| --- | --- |
| NamedElement.namespace, Namespace.ownedMember e le tre query strutturali Package con corpo true | Navigazione delle dichiarazioni di ownership/subset e filtraggio dei packagedElement; true non è un risultato del tipo dichiarato |
| Namespace.excludeCollisions | Il confronto è tra elementi distinti come dice la descrizione «each other», evitando di escludere ogni import per confronto con sé stesso |
| Namespace.importMembers | Il refuso mem.imp è interpretato come imp.isDistinguishableFrom(mem, self), secondo la descrizione sullo shadowing |
| NamedElement.allOwningPackages | L'identificatore p non legato è risolto seguendo i namespace Package consecutivi, come richiede la descrizione |
| NamedElement.qualifiedName | Le union tra stringhe indicano concatenazione; Set{} nel risultato String opzionale indica assenza (None) |
| Package.makesVisible/elements_public_or_private | Si usano le visibility dichiarate, secondo il testo, correggendo il confronto di un elemento con #public e i refusi ownedElements/visbility |
| TemplateBinding/TemplateSignature | I nomi template/templatedElement delle formule sono letti come i riferimenti dichiarati signature/template |
| Constraint e limiti con corpo true | Gli obblighi testuali Boolean, purezza e costanza sono verificati; nessun successo automatico per un'espressione sconosciuta |
| Constraint.value_specification_boolean | Si invoca booleanValue sulla specification e si richiede un bool Python esatto |
| OpaqueExpression.result | Si seleziona il solo parametro return come dice la descrizione della proprietà, non il primo parametro del comportamento |
| OpaqueExpression.value | La precondizione integral è rispettata; una valutazione numerica esterna richiede ancora un adapter, senza inventare un valore 0 |
| StringExpression.stringValue | I separatori corrotti della formula sono interpretati come stringa iniziale vuota e concatenazione, secondo il testo |

La collezione subExpression 2.4.1 è dichiarata unordered. Quando è usata per
concatenare, l'implementazione visita l'ordine conservato dalla rappresentazione;
non promette un risultato canonico indipendente dall'ordine per quella dichiarazione.

## Espressioni esterne e limiti dell'audit

```python
from Uml241.expression_semantics import register_expression_facts
register_expression_facts(expression, pure=True, constant=True)
```

I fatti sono forniti da codice/analyser fidato e restano nel registro 2.4.1;
non vengono ricavati dal nome del linguaggio o dal testo. Un fatto mancante resta
un'obbligazione unsupported. Non vengono eseguiti OCL o Behavior e non è implementato
un interprete generale per espressioni temporali o numeriche opache.

Resta il marker generale UML2.4.1.prose per la prosa supplementare non ancora
decomposta integralmente. Questo audit tratta le descrizioni delle regole del suo
ambito, non ogni frase dei PDF. Restano anche profili runtime, XMI e migrazione 2.4.1.
Il prossimo audit è Classification e SimpleClassifiers, necessario per chiudere
ereditarietà, inheritedMember, conformance e gli override delle query dei template.
