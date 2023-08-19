---
title: "Contribuire"
permalink: contribuire
---

# Testare il codice in locale

Per vedere il sito in locale, eseguire i seguenti comandi, e aprire `127.0.0.1:4000` nel browser. Si presuppone che abbiate installato [Docker](https://www.docker.com/) e [nodejs + npm](https://nodejs.org/en).

```bash
docker build -t informatica .
docker run --rm --volume="${PWD}:/srv/jekyll" --publish 4000:4000 informatica
```

Per `${PWD}` nella seconda riga viene usato per PowerShell... su Linux dovrebbe funzionare con `$PWD` o `$pwd`

In un terminale separato eseguire:

```bash
npm install # Solo la prima volta
npm run dev # Ogni volta che lavori sul progetto
```

Usa il seguente comando prima di fare commit

```
npm run build # Prima di fare il commit
```

## Icone 

I nomi delle icone li trovate su [Google Fonts](https://fonts.google.com/icons)


# Contribuire 

## Proposte / Bug

Se hai dei suggerimenti per migliorare il sito o vuoi rendere noto un bug o problema con il sito, apri una [ISSUE](https://github.com/sapienzastudentsnetwork/informatica/issues)

## Aggiungere contenuti

Se vuoi aggiungere dei contenuti, apri una [Pull Request](https://github.com/sapienzastudentsnetwork/informatica/pulls) con le modifiche che vuoi fare. Le modifiche saranno revisionate prima di essere salvate sul sito. Se non sai come fare, puoi seguire la [guida di GitHub](https://docs.github.com/en/get-started/quickstart/contributing-to-projects) per contribuire a progetti.

# Documentazione

Alcuni link utili
- [Liquid](https://shopify.github.io/liquid/) *(per templating)*
