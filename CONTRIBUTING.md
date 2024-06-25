---
title: "Contribuire"
permalink: contribuire
---

# Contribuire

## Clonare il Progetto

Per contribuire ai contenuti del sito, è necessario effettuare un **fork** del progetto e aprire una [**pull request**](https://github.com/sapienzastudentsnetwork/sapienzastudentsnetwork.github.io/pulls) con le modifiche proposte. Le modifiche saranno revisionate dai [curatori del progetto](/#curatori-del-progetto) prima di essere integrate nel sito. Se non hai familiarità con **git** e **GitHub**, puoi seguire la [guida di GitHub](https://docs.github.com/en/get-started/quickstart/contributing-to-projects) su come contribuire ai progetti, oppure chiedere aiuto a uno dei [curatori del progetto](/#curatori-del-progetto) o in uno dei [gruppi](./gruppi) disponibili.

## Avviare il Sito in Locale

Per avviare il sito in locale e testare il codice, segui i comandi elencati di seguito, e apri [localhost:4000](http://localhost:4000/) nel browser. È necessario avere installato [**Docker**](https://www.docker.com/) e [**Node.js**](https://nodejs.org/en).

```bash
npm install # Solo la prima volta
sudo npm run dev # Ogni volta che lavori sul progetto
```

Per interrompere l'esecuzione, basta premere `Ctrl+C` nel terminale, e [terminare il container Docker](https://docs.docker.com/engine/reference/commandline/stop/).

> Le modifiche a `_config.yml` richiedono la riesecuzione di `npm run dev`

Su **Windows** bisogna usare:

```bash
npm run dev-windows
```


## Proposte / Bug

Se hai dei suggerimenti per migliorare il sito o vuoi rendere noto un bug o problema con il sito, apri una [ISSUE](https://github.com/sapienzastudentsnetwork/sapienzastudentsnetwork.github.io/issues)


## Documentazione

Alcuni link utili
- Per i contenuti delle pagine, GitHub Pages utilizza [**Markdown**](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax);
- [**Jekyll**](https://jekyllrb.com/docs/pages/) è il *generatore di siti statici* utilizzato da GitHub;
- Jekyll utilizza [**Liquid**](https://shopify.github.io/liquid/) per il templating server-side *(offre l'accesso all'intestazione dei file markdown)*.

### Icone 

I nomi delle icone possono essere trovati su [Google Fonts](https://fonts.google.com/icons)
