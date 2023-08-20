---
title: "Contribuire"
permalink: contribuire
---

# Contribuire

## Clonare il progetto

Se vuoi aggiungere dei contenuti, devi fare il **fork** del progetto e aprire una [**pull request**](https://github.com/sapienzastudentsnetwork/informatica/pulls) con le modifiche che vuoi fare. Le modifiche saranno revisionate prima di essere salvate sul sito. Se non sai usare bene **git** e **GitHub** puoi seguire la [guida di GitHub](https://docs.github.com/en/get-started/quickstart/contributing-to-projects) su come contribuire a progetti, o chiedere aiuto su uno dei [gruppi](./gruppi).

## Aprire il sito in locale

Per aprire il sito in locale e testare il codice, bisogna eseguire i comandi di seguito elencati, e aprire [localhost:4000](http://localhost:4000/) nel browser. È necessario aver installato [**Docker**](https://www.docker.com/) e [**Node.js**](https://nodejs.org/en).

```bash
npm install # Solo la prima volta
npm run dev # Ogni volta che lavori sul progetto
```

Per interrompere l'esecuzione, basta premere `Ctrl+C` nel terminale, e [terminare il container Docker](https://docs.docker.com/engine/reference/commandline/stop/).

> Le modifiche a `_config.yml` richiedono la riesecuzione di `npm run dev`

Su **Windows** bisogna usare 

```bash
npm run dev-windows
```


## Proposte / Bug

Se hai dei suggerimenti per migliorare il sito o vuoi rendere noto un bug o problema con il sito, apri una [ISSUE](https://github.com/sapienzastudentsnetwork/informatica/issues)


## Documentazione

Alcuni link utili
- Per i contenuti delle pagine, GitHub Pages usa [Markdown](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
- [**Jekyll**](https://jekyllrb.com/docs/pages/) è il *static site generator* usato da GitHub.
- Jekyll usa [**Liquid**](https://shopify.github.io/liquid/) per templating server-side *(vi da l'accesso all'instestazione dei file markdown)*

### Icone 

I nomi delle icone li trovate su [Google Fonts](https://fonts.google.com/icons)
