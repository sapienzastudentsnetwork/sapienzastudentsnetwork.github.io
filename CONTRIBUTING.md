# Come Contribuire

> [!NOTE]
> La pagina integrale e più interattiva su come contribuire è consultabile [presso il sito stesso](https://sapienzastudents.net/it/contribuire/come-contribuire/)

Questo progetto è immenso, e non sempre lo staff che ci lavora può occuparsene. È un progetto nato dagli studenti per gli studenti, quindi ogni possibile aiuto è apprezzato. Vuoi dare una mano? Segui questa guida per sapere come puoi contribuire!

Per contribuire è possibile utilizzare **GitHub**, quindi è importante conoscere un po' le basi (principalmente cos'è **git**, come eseguire **fork** e **clone** di una repo, cosa sono i **commits** e le **pull requests**). Se non te la senti di farlo tramite la **CLI** (Command Line Interface), puoi farlo tramite VSCode o il tuo editor preferito. In questa guida vedrai come farlo tramite CLI, in modo da imparare qualcosa su come funziona **git**.

> [!NOTE]
> **Regole per contribuire e per le Pull Requests**
>
> Puoi trovare maggiori informazioni su come fare una corretta pull request [**qui**](https://github.com/sapienzastudentsnetwork/sapienzastudentsnetwork.github.io/pulls)
>
> Se non sei familiare con **git** e **GitHub**, puoi seguire la [guida di GitHub](https://docs.github.com/en/get-started/quickstart/contributing-to-projects) su come contribuire ai progetti degli altri, o eventualmente chiedere aiuto allo [staff del progetto](/it/contribuire/contatti) o in uno dei [gruppi disponibili](/it/canali/gruppi).

## Clonare il progetto

Per contribuire allo sviluppo del sito, devi creare un **fork** del progetto e modificarlo. Una volta effettuata la modifica, puoi aprire una **pull request** e inviarci le tue modifiche. Vediamo come fare:

1. Su GitHub, apri la [**repository del sito**](https://github.com/sapienzastudentsnetwork/sapienzastudentsnetwork.github.io) e crea un fork tramite il pulsante in alto a destra. Puoi chiamarlo come vuoi, non influirà sulla repo originale;
2. Una volta creato il fork, devi **clonarlo in locale**. Prima di clonarlo, devi copiare l'indirizzo del repository: sulla pagina del fork che hai appena creato, clicca sul pulsante verde "**<i class="fa-solid fa-code" style="color: #63E6BE;"></i> Code**" che trovi in alto sulla pagina e copia l'URL `https` che dovrebbe terminare in `.git` dalla finestra pop-up appena aperta;
3. Apri un terminale e naviga in una cartella dove vuoi clonare il fork. Una volta scelta la cartella, digita `git clone --recurse-submodules` e poi incolla il tuo URL dopo il comando. Vedrai qualcosa del tipo:
```bash
git clone --recurse-submodules https://github.com/<tuo_username>/<nome_fork>.git
```
Ora hai clonato il fork localmente, il che significa che aprendo un editor di testo puoi iniziare a modificare i file del sito.

## Avviare il sito localmente

Ci sono due modi per eseguire il sito localmente. Uno è utilizzando i **binaries di Hugo**, l'altro è usando **Docker**. Anche se forniscono le stesse funzioni, Docker potrebbe essere uno strumento difficile se lo usi per la prima volta. Ti incoraggiamo a provarlo, ma se non te la senti puoi semplicemente usare i binaries di Hugo:

### Usare Hugo

Prima di iniziare, verifica se hai installato i [binaries di Hugo](https://gohugo.io/installation/).

4. Mentre sei ancora nella cartella del repository, puoi eseguire localmente il sito con
```bash
hugo server
```

> [!WARNING]
> Se hai ricevuto un errore come il seguente
> ```txt
> Error: error building site: process: readAndProcessContent: "/home/<user>
> /SapienzaStudentsNetworkFork/it/canali/discord.md:7:1": failed to extract
> shortcode: template for shortcode "button" not found
> ```
> significa che il tema del sito non è stato clonato correttamente. Per risolvere questo problema, hai due modi:
> 1. Rimuovi da git la cartella del tema con:
> ```bash
> git rm themes/hugo-book
> ```
> 
> 2. Rimuovi la cartella del tema. Su sistemi UNIX-like, puoi eseguire:
> ```bash
> rm -rf themes/hugo-book
> ```
> 
> 3. Installa nuovamente il tema con git, utilizzando il seguente comando:
> ```bash
> git submodule add https://github.com/alex-shpak/hugo-book themes/hugo-book
> ```
> 
> Ora il problema dovrebbe essere scomparso e dovresti essere in grado di buildare il sito senza problemi.

5. Apri [`localhost:1313`](http://localhost:1313/) nel tuo browser ed ecco fatto! Ora puoi visualizzare il sito in tempo reale. Poiché Hugo supporta il ricaricamento automatico, ogni volta che un file cambia, cambierà anche il sito.

6. Se vuoi fermare il server, premi semplicemente `Ctrl + C` nel terminale.

### Usare Docker

Prima di iniziare, verifica se hai installato [**Docker**](https://www.docker.com/).

4. Per eseguire il sito localmente e testare il tuo codice, esegui i seguenti comandi:
```bash
docker build -t hugo-site . # Solo la prima volta che cloni il fork
sudo docker run --rm -p 1313:1313 -v $(pwd):/app hugo-site # Ogni volta che lavori sul progetto
```

5. Apri [`localhost:1313`](http://localhost:1313/) nel browser ed ecco fatto! Ora puoi visualizzare il sito.
6. Se vuoi fermare il server, premi semplicemente `Ctrl+C` nel terminale.

## Proposte / Bug

Se hai suggerimenti per migliorare il sito, o vuoi segnalare un bug, puoi aprire un [issue](https://github.com/sapienzastudentsnetwork/sapienzastudentsnetwork.github.io/issues) sul repository GitHub (**NON** sul tuo fork!). Grazie in anticipo per qualsiasi aiuto tu possa darci!
