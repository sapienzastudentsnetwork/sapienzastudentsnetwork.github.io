---
title: Software Necessario
weight: 7
---

# Software Necessario

Durante il corso di laurea sarà necessario scaricare dei software e se siete alle prime armi con un computer potrebbe essere difficile capire cosa dovete fare.

{{% hint info %}}
<i class="fa-solid fa-circle-info" style="color: #74C0FC;"></i> **Sistemi Operativi e Versioni Software**

Questa guida sarà diversa in alcuni punti a seconda del sistema operativo che avete installato sul vostro computer, in questi casi troverete delle diverse schede ognuna per un diverso sistema.

Se notate qualche differenza negli screenshot presenti nella guida è perché non possiamo aggiornarla ad ogni nuova versione dei software richiesti. I procedimenti dovrebbero comunque rimanere simili.

{{% /hint %}}

---

## Python

Lo userete principalmente per il corso di **Fondamenti di Programmazione** ma vi tornerà estremamente utile anche per corsi come **Algoritmi 1 e 2**.

Per il corso di Fondamenti di Programmazione vi servirà:
- Una versione di Python, preferibilmente almeno la 3.12
- Un IDE (o anche un editor di testo per programmare), in questo vi viene data libertà dal docente ma in sede d'esame troverete installati soltanto [Spyder](https://www.spyder-ide.org/), [VS Code](https://code.visualstudio.com/) e [PyCharm](https://www.jetbrains.com/pycharm/).

In questa guida ci soffermeremo su l'installazione di Python. Il docente vi suggerirà di scaricare Python tramite [Anaconda](https://www.anaconda.com/) che vi permette di gestire le versioni installate, le librerie aggiuntive e gli ambienti virtuali tramite un interfaccia grafica. Inoltre, vi permette anche di scaricare l'IDE Spyder.

{{% hint info %}}
<i class="fa-solid fa-circle-info" style="color: #74C0FC;"></i> **Cosa cambia fra Conda e Anaconda**

Visto che la guida si incentra su questo, vediamo le differenze:
- "Anaconda" è il pacchetto completo che comprende oltre al package manager Conda anche altri strumenti.
- "Conda" è un package manager di Python che useremo come alternativa a quello base. Python ha infatti come package manager PyPi (o `pip`)

{{% /hint %}}

Potete quindi scegliere due metodi di installazione:
- Installare Python tramite la versione completa di Anaconda
- Usare una versione più piccola chiamata Miniconda che comprende comunque il package manager

---

### 1) Installazione con Anaconda
1) Andate sulla [pagina di download](https://www.anaconda.com/download/success) di Anaconda e scaricate la versione dedicata al vostro sistema operativo. Se avete un Mac fate attenzione a scegliere la giusta versione per l'architettura della CPU:
	- Per M1, M2, M3, M4.... scegliete **Apple Silicon**
	- Se avete un processore intel allora **Intel-Chip**
2) Eseguite l'installer appena scaricato e seguite le indicazioni

{{% hint warning %}}
<i class="fa-solid fa-triangle-exclamation" style="color: #FFD43B;"></i> **Windows: Aggiungere Conda a `PATH`**

Se siete su Windows, l'installer vi chiederà se volete aggiungere Conda a `PATH` (variabili di sistema / ambiente).

Le variabili d'ambiente servono al sistema per ricordare dove sono salvate determinate applicazioni in modo da usarle più facilmente dal terminale. Anaconda vi suggerirà di non aggiungerlo alle variabili d'ambiente.

Se non lo fate avrete un terminale dedicato a Conda ed uno normale ma potrebbe essere confusionario e scomodo da usare. Personalmente consiglio di aggiungerlo in modo da avere tutto in terminale.

{{% /hint %}}

3) Controllare che Conda sia installato:

{{% tabs "condacheck" %}}
{{% tab "Windows" %}}

Se avete aggiunto Conda alle variabili d'ambiente potete usare il comando da qualsiasi terminali mentre se non lo avete fatto dovrete aprire dal vostro menù delle app un Anaconda Prompt:

```bash
conda --version
```

Se è andato tutto bene verrà stampata sul terminale una stringa simile a questa `conda 24.1.2`.

{{% /tab %}}
{{% tab "Linux / macOS" %}}

Aprite un terminale e scrivete il seguente comando:

```bash
conda --version
```

Dovreste vedere un output simile a questo:

<img width="90%" style="margin-left: 5%; box-shadow: 5px 5px 30px rgba(0, 0, 0, 0.75)" src="https://i.imgur.com/6afvZ7w.png">

{{% /tab %}}
{{% /tabs %}}

4) Abbiamo finito! Puoi passare alla sezione successiva dove vedremo come installare le librerie necessarie e creare un ambiente virtuale.

---

### 2) Installazione con Miniconda

{{% tabs "minicondainstall" %}}
{{% tab "Windows" %}}

1) Andate sulla [pagina di download](https://www.anaconda.com/download?utm_source=anacondadocs&utm_medium=documentation&utm_campaign=download&utm_content=installwindows) e scaricate l'installer con miniconda
2) Avviate l'installer e seguite le istruzioni
3) Se vi tornano comode potete scegliere di creare un collegamento nel menù Start per Anaconda Prompt
4) Scegliete se aggiungere conda a PATH come visto nella sezione precedente. (Consigliato per avere un solo terminale)
5) Vi chiederà se volete registrare conda come Python predefinito per altri programmi, ve lo consiglio.
6) Finito! Potete aprire un Anaconda Prompt o un terminale qualsiasi e verificare che l'installazione sia andata a buon fine con: 

```bash
conda --version
```

{{% /tab %}}
{{% tab "macOS" %}}

1) Potete eseguire un'installazione più veloce inviando i seguenti comandi da un terminale:

Per processori **Apple Silicon** (M1, M2, M3, M4...)

```bash
mkdir -p ~/miniconda3
curl https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh -o ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm ~/miniconda3/miniconda.sh
```

Per processori **Intel**

```bash
mkdir -p ~/miniconda3
curl https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -o ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm ~/miniconda3/miniconda.sh
```

2) Una volta finito aggiornate il terminale con:

```bash
source ~/miniconda3/bin/activate
```

3) Fate in modo che conda si avvii ogni volta quando aprite un terminale:

```bash
conda init --all
```

{{% /tab %}}
{{% tab "Linux" %}}

1) Potete eseguire un'installazione più veloce inviando i seguenti comandi da un terminale:

Per processori **64bit**:

```bash
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm ~/miniconda3/miniconda.sh
```

Per processori **AWS Graviton 2/ARM 64**:

```bash
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm ~/miniconda3/miniconda.sh
```

Per processori **IBM Z**:

```bash
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-s390x.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm ~/miniconda3/miniconda.sh
```

2) Una volta finito aggiornate il terminale con:

```bash
source ~/miniconda3/bin/activate
```

3) Fate in modo che conda si avvii ogni volta quando aprite un terminale:

```bash
conda init --all
```

{{% /tab %}}
{{% /tab %}}

### 3) Creare un Ambiente Virtuale
Invece di installare tutte le librerie direttamente su conda andremo a creare un ambiente separato dedicato al corso, in questo modo se in futuro vorrete fare diversi progetti in Python potrete usare diverse versioni di Python e di librerie senza che vadano in conflitto tra di loro. Potete immaginarli come "computer diversi" tutti sul vostro PC che contengono solamente una versione di Python e delle librerie, la comodità è che potete scegliere fra questi con un semplice comando.

1) Creiamo l'ambiente "fondamenti" con il comando:

```bash
conda create -n fondamenti python=3.12
```

2) Il terminale scaricherà tutto il necessario, è possibile che vi venga chiesto di dare delle conferme.

3) Una volta terminato potete entrare nell'ambiente con:

```bash
conda activate fondamenti
```

-  `conda activate <nome ambiente>` serve ad entrare in un ambiente
- `conda deactivate` vi riporta nell'ambiente base, se già vi trovate in questo uscirete da l'ambiente conda.

### 4) Installare le librerie necessarie
Per il corso sono necessarie delle librerie utili per eseguire dei test automatici, conda serve proprio a semplificare questo passaggio.

Le librerie necessarie sono:

| Pacchetto          | Descrizione                                                                                                                            |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| `ddt`              | Permette di eseguire test descritti in un file JSON                                                                                    |
| `pytest-timeout`   | Permette di applicare un timeout all'esecuzione di ogni test                                                                           |
| `stopit`           | Permette di applicare un timeout all'esecuzione di una singola funzione                                                                |
| `pytest-profiling` | Permette di calcolare il tempo necessario per eseguire ogni funzione                                                                   |
| `radon`            | Permette di calcolare la [complessità ciclomatica](https://radon.readthedocs.io/en/latest/intro.html#cyclomatic-complexity) del codice |
| `typeguard`        | Permette di verificare che i tipi dei parametri e dei valori di ritorno di una funzione siano rispettati                               |
| `pandas`           | Libreria Python utilizzata per gestire e manipolare dati                                                                               |


Potete installare tutte queste con un solo comando, **assicuratevi di stare nell'ambiente creato precedentemente**:

```bash
conda install -c conda-forge ddt pytest-timeout stopit pytest-profiling radon typeguard pandas
```

Inoltre potete aggiornare tutti i pacchetti installati nell'ambiente con:

```bash
conda update --all
```

{{% hint info %}}
<i class="fa-solid fa-circle-info" style="color: #74C0FC;"></i> **IDE Spyder**

Alcuni docenti a lezione utilizzano l'IDE Spyder, se volete installarlo anche voi va fatto tramite Conda con il seguente comando:

```bash
conda install -c conda-forge spyder spyder-unittest pylsp-mypy
```

Oltre a Spyder, questo comando installerà anche dei tool aggiuntivi per quest'ultimo.

{{% /hint %}}
