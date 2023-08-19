---
title: "Contributing"
permalink: /Contributing/
---

# Contributing

Per aggiornare i contenuti

```bash
git submodule update --init --recursive --remote
```

Per vedere il sito in locale, eseguire i seguenti comandi, e aprire `127.0.0.1:4000` nel browser. Si presuppone che abbiate installato [Docker](https://www.docker.com/).

```bash
docker build -t sapienza-informatica .
docker run --rm --volume="${PWD}:/srv/jekyll" --publish 4000:4000 sapienza-informatica
```

Per `${PWD}` nella seconda riga viene usato per PowerShell... su Linux dovrebbe funzionare con `$PWD` o `$pwd`

In un terminale separato eseguire:

```bash
npm install # Solo la prima volta
npx tailwindcss -i ./assets/css/app.css -o ./assets/css/tailwind.css --watch
```

Usa il seguente comando prima di fare commit

```
npx tailwindcss -i ./assets/css/app.css -o ./assets/css/tailwind.css --minify
```
