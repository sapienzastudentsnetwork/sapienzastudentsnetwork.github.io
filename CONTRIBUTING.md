# Come contribuire

> [!NOTE]
> **English readers:** this document is written in Italian. Please refer to the [complete interactive contribution guide in English](https://sapienzastudents.net/how-to-contribute/).

> [!NOTE]
> La versione più completa e interattiva di questa guida è disponibile anche [sul sito](https://sapienzastudents.net/how-to-contribute/).

SapienzaStudents.net è un progetto costruito **da studenti e studentesse, per studenti e studentesse**. Riunisce informazioni pratiche spesso sparse tra molte fonti e le trasforma in guide, strumenti e risorse condivise usate da migliaia di persone. Per mantenere accurato e utile un progetto di queste dimensioni serve una comunità: **anche una piccola correzione può evitare dubbi e far risparmiare tempo a moltissimi studenti**.

Per contribuire non devi essere uno sviluppatore, installare programmi o avviare il sito in locale. Correggere un refuso, aggiornare una scadenza, chiarire un paragrafo poco comprensibile, sostituire un link non più valido o proporre una guida mancante sono tutti contributi preziosi.

> [!TIP]
> **Scegli il percorso più semplice**
>
> - **Piccola modifica ai contenuti:** usa il pulsante di modifica della pagina e l'editor web di GitHub;
> - **Segnalazione, informazione non aggiornata o bug:** apri una issue. Non serve sapere quale file modificare;
> - **Modifica più ampia ai contenuti o al codice:** usa un fork e, quando è utile, avvia il sito in locale
>
> L'ambiente di sviluppo locale è una possibilità, non un requisito per iniziare.

## Contributo rapido: modifica una pagina dal browser

Per la maggior parte delle correzioni a testi e link, questo è il percorso consigliato. Serve soltanto un account GitHub gratuito.

1. Apri su SapienzaStudents.net la pagina che vuoi migliorare;
2. Usa il link **modifica pagina** o il pulsante con la matita presente nella pagina. Se il contenuto è composto da più file condivisi, il sito potrebbe mostrarti più sorgenti: scegli quella che contiene il testo da correggere;
3. GitHub aprirà il file Markdown corretto. Se richiesto, premi **Fork this repository** per creare automaticamente una tua copia del progetto;
4. Premi l'icona della matita, effettua la modifica e controlla il risultato nella scheda **Preview**;
5. Seleziona **Propose changes**, descrivi brevemente cosa hai cambiato e apri la pull request

Hai finito. GitHub gestisce per te fork, branch e pull request; chi mantiene il progetto potrà controllare la modifica prima della pubblicazione. Per una piccola correzione ai contenuti **non** devi clonare il repository, usare il terminale, installare Hugo o compilare il sito.

> [!NOTE]
> **Il contenuto può trovarsi in un altro repository**
>
> Alcune guide sono condivise tramite submodule Git. Il link di modifica della pagina porta al repository che contiene davvero il testo: seguilo invece di cercare manualmente il file nel repository principale.

## Segnala un problema o proponi un'idea

Se non sai come correggere un problema, oppure vuoi avanzare una proposta senza preparare direttamente la modifica, [apri una issue](https://github.com/sapienzastudentsnetwork/sapienzastudentsnetwork.github.io/issues) nel repository principale.

Indica, se possibile:

- l'indirizzo della pagina interessata;
- cosa manca o risulta errato o poco chiaro;
- l'informazione corretta e una fonte autorevole, quando pertinente;
- screenshot o passaggi per riprodurre il problema, nel caso di un bug

Puoi anche chiedere aiuto allo [staff del progetto](https://sapienzastudents.net/sapienza-students-network/#sapienzastudentsnet) oppure unirti alla [chat dedicata allo sviluppo del sito](https://t.me/addlist/8jXnS8NuTsxkMDlk). Una segnalazione precisa è già un contributo utile.

## In che modo puoi contribuire

I contributi non riguardano soltanto il codice. Puoi, ad esempio:

- correggere refusi, grammatica, formattazione e link non funzionanti;
- aggiornare date, procedure, contatti e informazioni sui corsi;
- rendere più chiara una spiegazione o migliorare la versione italiana o inglese;
- aggiungere una risorsa utile, una FAQ, una relazione di tirocinio o una guida mancante;
- migliorare accessibilità, grafica, template, automazioni o dati;
- segnalare un problema e aiutare a verificare le informazioni

Quando una pagina esiste in entrambe le lingue, se possibile aggiorna tutte e due le versioni mantenendone allineato il significato. Meglio una formulazione naturale e adatta al contesto che una traduzione letterale. Se puoi intervenire soltanto su una lingua, scrivilo nella pull request: qualcun altro potrà completare la localizzazione.

## Prima di inviare il contributo

Un buon contributo è mirato e facile da verificare:

- separa in pull request diverse le modifiche non collegate tra loro;
- spiega **cosa** hai cambiato e **perché**;
- conserva front matter, shortcode e struttura Markdown circostante;
- controlla i link e usa l'anteprima del testo formattato;
- non inserire dati personali, contenuti riservati o materiale protetto senza autorizzazione;
- per informazioni amministrative o soggette a scadenza, indica una fonte ufficiale o affidabile;
- usa un linguaggio chiaro, accogliente e inclusivo

Puoi consultare le [pull request aperte](https://github.com/sapienzastudentsnetwork/sapienzastudentsnetwork.github.io/pulls) per vedere alcuni esempi. Se durante la revisione ti vengono richieste modifiche, è una normale parte del lavoro collaborativo.

> [!TIP]
> **Chi ha contribuito al progetto**
>
> Visita la pagina dei [contributori](https://sapienzastudents.net/contributors/) per scoprire chi ha aiutato a far crescere la wiki e il sito nel suo insieme. Ogni contributo accettato, grande o piccolo, entra a far parte di una risorsa che la comunità studentesca può continuare a migliorare insieme.

## Procedura completa in locale

Usa questa procedura per modifiche ampie, interventi sul codice o sulla struttura e per tutto ciò che vuoi verificare localmente. È utile conoscere le basi di Git, fork, commit e pull request, ma puoi impararle strada facendo.

### 1. Crea un fork e clona il repository

1. Apri il [repository del sito](https://github.com/sapienzastudentsnetwork/sapienzastudentsnetwork.github.io) e seleziona **Fork**;
2. Clona il tuo fork includendo i submodule:

```bash
git clone --recurse-submodules https://github.com/<tuo-username>/sapienzastudentsnetwork.github.io.git
cd sapienzastudentsnetwork.github.io
```

Se hai già clonato il progetto senza submodule, inizializzali con:

```bash
git submodule update --init --recursive
```

3. Crea un branch dal nome descrittivo:

```bash
git switch -c migliora-guida-contributi
```

4. Effettua le modifiche e controllale prima del commit:

```bash
git status
git diff
```

### 2. Avvia il sito in locale, se serve

L'anteprima locale è fortemente consigliata per modifiche a template, stile, script, navigazione o formattazione complessa. Di solito non è necessaria per una piccola correzione testuale effettuata dall'editor di GitHub.

### Docker Compose

Installa [Docker](https://www.docker.com/) con Docker Compose, quindi esegui:

```bash
docker compose up --build
```

Apri [`localhost:1313`](http://localhost:1313/) nel browser. Ferma il sito con `Ctrl+C`; se lo hai avviato in modalità detached, usa `docker compose down`.

Docker genera automaticamente i metadati delle sorgenti delle pagine. Per saltare questo passaggio in una singola esecuzione:

```bash
GENERATE_SOURCE_METADATA=false docker compose up --build
```
### Hugo

Installa una versione di Hugo compatibile con il repository e le dipendenze front-end del progetto. Dalla cartella principale esegui:

```bash
npm install
npm run build
hugo server
```

Apri [`localhost:1313`](http://localhost:1313/). Hugo aggiorna la pagina quando i file cambiano; premi `Ctrl+C` per fermarlo.

Il sito funziona con i metadati Git nativi di Hugo. Per verificare anche i link di modifica e le informazioni sull'ultimo aggiornamento dei contenuti inclusi da altri file o submodule, genera prima il data file locale facoltativo:

```bash
python3 _scripts/generate-page-source-metadata.py
hugo server
```

Il file generato `data/page_source_metadata.json` è ignorato da Git.

### 3. Crea il commit e apri una pull request

```bash
git add <file-modificati>
git commit -m "docs: migliora la guida ai contributi"
git push -u origin migliora-guida-contributi
```

Apri il link mostrato da Git, oppure visita il tuo fork su GitHub, e crea una pull request verso il branch `main` del repository principale. Nella descrizione riassumi la modifica, spiega come l'hai verificata e collega eventuali issue correlate.

## Hai bisogno di aiuto?

Non lasciare che uno strumento che non conosci ti impedisca di migliorare il progetto. Puoi [aprire una issue](https://github.com/sapienzastudentsnetwork/sapienzastudentsnetwork.github.io/issues), inviare direttamente il testo che proponi o chiedere indicazioni alla comunità. Chi mantiene il sito può aiutarti a trasformare una buona osservazione in un contributo completo.
