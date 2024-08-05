# Usa un'immagine di base di Ubuntu
FROM ubuntu:latest

# Imposta la variabile d'ambiente per non chiedere interattività
ENV DEBIAN_FRONTEND=noninteractive

# Aggiorna il sistema e installa i pacchetti necessari
RUN apt-get update && apt-get install -y \
    wget \
    dpkg \
    npm \
    git \
    curl \
    && apt-get clean

# Installa Hugo
ENV HUGO_VERSION 0.126.0

RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        wget -O /tmp/hugo.deb https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-amd64.deb; \
    elif [ "$ARCH" = "aarch64" ]; then \
        wget -O /tmp/hugo.deb https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-arm64.deb; \
    else \
        echo "Unsupported architecture: $ARCH"; exit 1; \
    fi && \
    dpkg -i /tmp/hugo.deb && \
    rm /tmp/hugo.deb

# Installa Dart Sass
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        curl -L https://github.com/sass/dart-sass/releases/download/1.56.1/dart-sass-1.56.1-linux-x64.tar.gz -o dart-sass.tar.gz; \
    elif [ "$ARCH" = "aarch64" ]; then \
        curl -L https://github.com/sass/dart-sass/releases/download/1.56.1/dart-sass-1.56.1-linux-arm64.tar.gz -o dart-sass.tar.gz; \
    else \
        echo "Unsupported architecture: $ARCH"; exit 1; \
    fi && \
    tar -xzf dart-sass.tar.gz && \
    mv dart-sass /usr/local/bin/ && \
    ln -s /usr/local/bin/dart-sass/sass /usr/local/bin/sass && \
    rm dart-sass.tar.gz

# Configura Git per considerare /app come una directory sicura
RUN git config --global --add safe.directory /app

# Copia i file del progetto nella directory /app
WORKDIR /app
COPY . .

# Installa le dipendenze Node.js se il file package-lock.json o npm-shrinkwrap.json esiste
RUN if [ -f package-lock.json ] || [ -f npm-shrinkwrap.json ]; then npm ci; fi

# Espone la porta per il server Hugo
EXPOSE 1313

# Comando per avviare il server di sviluppo Hugo
CMD ["hugo", "server", "--disableFastRender", "--bind", "0.0.0.0"]
