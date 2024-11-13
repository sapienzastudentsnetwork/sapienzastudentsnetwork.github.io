# Sapienza Fast Charge

{{% hint info %}}
<i class="fa-solid fa-circle-info" style="color: #74C0FC;"></i> **Riguardo questa pagina**

Per il contenuto di questa pagina abbiamo coinvolto direttamente il team trattato, il che corrisponde, quindi, ad una loro presentazione dello stesso.
{{% /hint %}}

**Sapienza Fast Charge** è il team di Formula Student Electric dell’Università Sapienza. Il nostro team unisce competenze accademiche e pratiche per progettare, costruire e gareggiare con monoposto elettriche ad alte prestazioni. La nostra missione è spingerci oltre i confini della tecnologia dei veicoli elettrici e promuovere pratiche di corsa sostenibili.

## DV Car 2024

### Overview

La **DV Car 2024** rappresenta il nostro più recente progresso nella progettazione di veicoli elettrici e autonomi, frutto di due anni di sviluppo dedicato. Questo veicolo elettrico a guida autonoma integra tecnologie avanzate di sensori e soluzioni software all’avanguardia, affrontando le sfide del controllo autonomo.

### Componenti Chiave

#### Architettura a Microservizi

Il nostro software è strutturato con un'**architettura basata su microservizi**, ciascun compito essenziale per la guida autonoma viene gestito in un servizio dedicato distinto. Questi servizi operano in modo indipendente e comunicano tramite un message broker. Questa architettura garantisce:

- Allocazione efficiente delle risorse per l'elaborazione in parallelo
- Robustezza contro guasti critici, poiché il fallimento di un microservizio non influenza l'intero sistema

#### Principali Microservizi

1. **Computer Vision**:  
   Il modulo di computer vision identifica i coni del tracciato utilizzando una telecamera di profondità che sfrutta sensori a infrarossi per misurare la distanza dei coni. Le funzionalità principali includono:
   - **Rilevamento dei Coni**: Determina le posizioni dei coni nello spazio
   - **Riconoscimento del Colore**: Fondamentale per la stima della traiettoria
   - **Filtraggio degli Errori**: Scarta coni con anomalie di colore o distanza

2. **Sensor Fusion & SLAM (Simultaneous Localization and Mapping)**:  
   Questo sistema integra dati da più sensori — accelerometro, giroscopio, magnetometro, GPS e Lidar — per una navigazione precisa. SLAM svolge due compiti principali:
   - **Mappatura**: Costruisce una mappa utilizzando dati dei sensori e posizioni dei coni individuati dalla computer vision
   - **Localizzazione**: Determina la posizione attuale del veicolo nella mappa, permettendo la pianificazione in tempo reale della traiettoria

3. **Path Planning**:  
   Questo componente utilizza i dati dei coni dalla visione artificiale per calcolare una traiettoria sicura ed efficiente per il veicolo, minimizzando il tempo sul giro. Si avvale di tecniche come triangolazioni e interpolazioni per ottimizzare il percorso.

4. **High-Level Control (HLC)**:  
   L’HLC coordina le funzioni degli attuatori (sterzo, acceleratore e freni) basandosi sui dati forniti dal pianificatore di percorso e da SLAM. Questo modulo utilizza algoritmi di deep reinforcement learning per perfezionare i segnali di controllo e garantire una precisa esecuzione della traiettoria.

### Prospettive Future

Sapienza Fast Charge continua a innovare nella tecnologia dei veicoli elettrici e autonomi. Con costante ricerca e sviluppo, puntiamo a migliorare le prestazioni, aumentare la sicurezza e contribuire a un futuro sostenibile per il motorsport.

---

**Unisciti a noi** in questo entusiasmante viaggio all’avanguardia delle corse sostenibili e ad alta tecnologia!
