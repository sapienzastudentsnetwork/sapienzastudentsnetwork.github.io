# SapienzaStudents.net

> **La wiki open source realizzata da studenti e studentesse per orientarsi, studiare e vivere appieno l'università.**

[Visita il sito](https://sapienzastudents.net/) · [Scopri come contribuire](https://sapienzastudents.net/how-to-contribute/) · [Segnala un problema](https://github.com/sapienzastudentsnetwork/sapienzastudentsnetwork.github.io/issues)

SapienzaStudents.net raccoglie in **un unico portale** le informazioni che più spesso risultano frammentate: **immatricolazione, insegnamenti, orari e calendari, esami, piani di studio, tirocini, laurea e servizi**, insieme a **gruppi e risorse condivise** dalla comunità. Il progetto copre diversi corsi afferenti al **Dipartimento di Informatica** e altre comunità studentesche, come quella del [Dipartimento di Filosofia](https://sapienzastudents.net/filosofia/), con contenuti in **italiano e inglese**.

È un progetto consolidato, cresciuto nel corso degli anni e coordinato da [Sapienza Students Network](https://sapienzastudents.net/sapienza-students-network/), organizzazione studentesca indipendente attiva dal 2021 che cura anche community, gruppi, forum e altri servizi digitali collaborativi per studenti e studentesse.

## 💡 Cosa offre

- **Guide pratiche**, dall'ingresso in Sapienza fino alla laurea
- **Strumenti interattivi** per orari, piano di studi e calcolo del voto di laurea
- **Community**: gruppi per corsi e insegnamenti, forum, risorse e contatti utili
- **Contenuti verificabili e migliorabili**: ogni pagina può essere corretta o ampliata tramite GitHub
- **Un progetto realmente utilizzato**: tra aprile 2025 e agosto 2026 ha superato **1,5 milioni di impressioni** e **27.000 clic** dalla Ricerca Google

Nel 2024 il network ha avviato una **collaborazione ufficiale con il Consiglio di Area Didattica (CAD) di Informatica**, contribuendo ad arricchire i contenuti e a far conoscere il portale alle nuove matricole. Il progetto è stato inoltre presentato a [OpenDI 2025](https://www.youtube.com/live/ycmIWcCQU8c?t=7503) e [OpenDI 2026](https://www.youtube.com/watch?v=omDUKDX2hOA).

## ⚙️ Tecnologia e automazioni

Il sito è generato staticamente con [**Hugo**](https://gohugo.io/) e il tema [**Hugo Book**](https://themes.gohugo.io/themes/hugo-book/), personalizzato con template, shortcode, JavaScript e Sass; [**Tailwind CSS**](https://tailwindcss.com/) è impiegato per la homepage. Dati strutturati e automazioni aggiornano orari, corsi, docenti e classifiche dei contributori; GitHub Actions gestisce build, pubblicazione e sincronizzazioni periodiche.

```bash
git clone --recurse-submodules https://github.com/sapienzastudentsnetwork/sapienzastudentsnetwork.github.io.git
cd sapienzastudentsnetwork.github.io
docker compose up --build
```

Il sito locale sarà disponibile su `http://localhost:1313`. Sono disponibili anche altre modalità di esecuzione, descritte nella [guida su come contribuire](https://sapienzastudents.net/how-to-contribute/).

## 🤝 Contribuisci

**Non serve essere sviluppatori**: puoi correggere un'informazione, aggiornare una scadenza, migliorare una guida, aggiungere una risorsa o proporre una nuova funzionalità. **Ogni contributo aiuta migliaia di studenti.**

Leggi [CONTRIBUTING.md](CONTRIBUTING.md), consulta la [guida interattiva](https://sapienzastudents.net/how-to-contribute/) oppure apri direttamente una [issue](https://github.com/sapienzastudentsnetwork/sapienzastudentsnetwork.github.io/issues).

## 📜 Licenza

Il progetto è distribuito con licenza [AGPL-3.0](LICENSE).

## 👥 Chi ha contribuito

<a href="https://github.com/sapienzastudentsnetwork/sapienzastudentsnetwork.github.io/graphs/contributors?all=1">
  <img src="https://contrib.rocks/image?repo=sapienzastudentsnetwork/sapienzastudentsnetwork.github.io" alt="Contributori di SapienzaStudents.net" />
</a>

[Visualizza l'elenco completo dei contributori](https://github.com/sapienzastudentsnetwork/sapienzastudentsnetwork.github.io/graphs/contributors?all=1).
