---
title: "Come contribuire"
aliases: ["/contribuire", "/informatica/contribuire"]
bookToC: false
---

# Contribuire

## Clonare il Progetto

Per contribuire ai contenuti del sito, è necessario effettuare un **fork** del progetto e aprire una [**pull request**](https://github.com/sapienzastudentsnetwork/sapienzastudentsnetwork.github.io/pulls) con le modifiche proposte. Le modifiche saranno revisionate dai [curatori del progetto](/it/contribuire/contatti) prima di essere integrate nel sito. Se non hai familiarità con **git** e **GitHub**, puoi seguire la [guida di GitHub](https://docs.github.com/en/get-started/quickstart/contributing-to-projects) su come contribuire ai progetti, oppure chiedere aiuto a uno dei [curatori del progetto](/it/contribuire/contatti) o in uno dei [gruppi](/it/canali/telegram) disponibili.

## Avviare il Sito in Locale

Per avviare il sito in locale e testare il codice, segui i comandi elencati di seguito, e apri [localhost:4000](http://localhost:4000/) nel browser. È necessario avere installato [**Docker**](https://www.docker.com/).

```bash
docker build -t hugo-site . # Solo la prima volta
sudo docker run --rm -p 1313:1313 -v $(pwd):/app hugo-site # Ogni volta che lavori sul progetto
```

Puoi interrompere l'esecuzione in qualsiasi momento premendo `Ctrl+C` nel terminale.

## Proposte / Bug

Se hai dei suggerimenti per migliorare il sito o vuoi rendere noto un bug o problema con il sito, puoi aprire una [ISSUE](https://github.com/sapienzastudentsnetwork/sapienzastudentsnetwork.github.io/issues) nel repository GitHub. Grazie mille in anticipo per il tuo contributo :-)
