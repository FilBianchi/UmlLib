# XMI UML 2.4.1 — 0.18.0

`Uml241.xmi` importa ed esporta modelli usando le classi pubbliche, enum,
associazioni, subset/redefinition e composizione del backend isolato 2.4.1.
`Uml251.xmi` seleziona esplicitamente 2.5.1. Non si esegue una conversione
cambiando soltanto i namespace.

```python
from Uml241.xmi import load, loads, dump, dumps

document = load('legacy.xmi')
assert document.semantic_version == '2.4.1'
model = document.roots[0]
model.name = 'Updated'
dump(document, 'updated.xmi')
restored = loads(dumps(document))
print(document.complete, document.diagnostics)
print(model.validate(recursive=True))
```

## Selezione della versione

L'API generica `umltools.xmi.load/loads` conserva il default 2.5.1 per compatibilità.
Per selezionare la versione prima di costruire gli oggetti:

```python
from umltools.xmi import load, dumps, detect_version

document = load('model.xmi', semantic_version='auto')
data = dumps(document)  # Usa la versione effettiva del modello/documento.
```

In alternativa `semantic_version='2.4.1'` seleziona il backend direttamente.
Le API versionate non cambiano backend: `Uml241.xmi` non importa/esporta modelli
2.5.1 e `Uml251.xmi` non importa/esporta modelli 2.4.1. Un target_version diverso
dalla versione del modello resta un errore, senza migrazione implicita.

La scelta automatica usa i namespace effettivamente usati dalle istanze, non
i prefissi o le dichiarazioni xmlns inutilizzate. `20110701` identifica 2.4.1;
`20161101` identifica 2.5.1. `20100901` è condiviso dai materiali 2.4/2.4.1;
`20131001` è condiviso da 2.5/2.5.1. I namespace Eclipse UML2 identificano un
dialetto, non una release UML esatta. Per questi casi occorre una scelta esplicita
o la dichiarazione di metamodel nella Extension UmlLib. Nessuna inferenza viene
fatta dal nome del file, da xmi:version o da exporterVersion.

L'export registra `<lib:metamodel version="2.4.1"/>` in una XMI Extension UmlLib.
Questa informazione è distinta da xmi:version, che descrive il trasporto. Versioni
esplicite contraddittorie o namespace incompatibili producono XmiVersionError,
anche con strict=False e anche nelle risorse dipendenti. Le eccezioni XmiError e
sottoclassi possono essere intercettate dall'API generica per entrambe le versioni.

L'output canonico 2.4.1 usa i namespace UML/XMI 20110701; il reader accetta anche
le forme legacy 20100901 della fonte. Provenienza: [catalogo OMG UML 2.4.1](https://www.omg.org/spec/UML/2.4.1)
e [specifica XMI 2.4.1](https://www.omg.org/spec/XMI/2.4.1/PDF).

## Contratto del grafo

Sono supportati identità xmi:id per risorsa, UUID, riferimenti in avanti/ciclici,
href/idref, librerie esterne fornite esplicitamente, risorse relative locali,
enum, valori scalari e collezioni, ownership, inversi e le differenze strutturali
2.4.1 di State, Region, Activity.structuredNode e LoopNode.loopVariable.
Un tipo PrimitiveType definito nel modello conserva identità e riferimenti;
un LiteralString tipizzato conserva il suo valore lessicale. I nomi Money,
EString o altri nomi di dominio non attivano alias o conversioni speciali.

L'export omette le cache derivate, sceglie un solo contenimento composito e
bundle=True chiude riferimenti e proprietari in un unico documento. Con
bundle=False, i riferimenti esterni richiedono identità importate o una mappa
external_references. Non si riscrive automaticamente un progetto multi-file.
L'import fallito ripristina gli oggetti esterni e rimuove quelli appena creati;
l'export serializza prima di scrivere il file. Nessun fetch di rete o interprete
OCL viene eseguito dal reader. DTD/entity e limiti di byte/elementi/profondità
sono controllati anche nella fase di selezione automatica.

## Profili ed estensioni

Le definizioni strutturali Profile, Stereotype, Extension e ProfileApplication
possono essere lette/scritte. L'applicazione runtime dei profili e i valori dei tag
2.4.1 sono ancora un contratto separato: strict=True li rifiuta; strict=False li
conserva come XML opaco, senza creare istanze applicate o dichiararli validati.
I MOF extension Tag del file OMG PrimitiveTypes vengono conservati con diagnostiche,
non interpretati come tag runtime di un profilo UML.

Per conservare le estensioni si esporta il documento, non soltanto le sue roots.
Il contenuto, gli attributi QName e i loro binding sono conservati; non si garantisce
identità byte per byte, né si riscrivono i riferimenti proprietari quando il bundle
rimappa ID duplicati. CMOF, frammenti EMF/XPointer e layout UMLDI restano fuori ambito.
Le callback Python e i fatti fidati sulle espressioni/esecuzione non sono trasportati.

complete=True indica assenza di lacune di decodifica registrate, non conformità UML.
I modelli incompleti possono essere decodificati: validate resta una verifica distinta.

## Evidenze

La suite completa contiene 409 test. I 17 casi XMI 2.4.1 includono uno sweep di
tutti i 549 setter osservabili con export/import e confronto della rappresentazione
normalizzata, oltre a grafi indipendenti, vincoli di versione, rollback e sicurezza.

La fixture OMG PrimitiveTypes originale ha checksum fissato nel manifest: 11 oggetti
UML e quattro Tag MOF conservati in modalità permissiva. Il namespace legacy ambiguo
viene interpretato con backend 2.4.1 esplicito. I cinque casi pubblici Spring passano
con 11, 20, 83, 43 e 76 oggetti, nessuna diagnostica e round-trip del grafo noto.
I loro namespace Eclipse non attestano la release UML del produttore: il test verifica
la compatibilità del sottoinsieme rappresentato con la scelta esplicita 2.4.1.

```console
python -m unittest discover -s tests -p test_xmi241.py -q
python -m scripts.verify_xmi_corpus --fetch --semantic-version 2.4.1
```

L'audit dichiarativo resta in UML241_AUDIT.md; XMI non chiude gli obblighi di prosa
generale, esecuzione/protocolli, PackageMerge, profili runtime o migrazione tra versioni.
