FROM hugomods/hugo:dart-sass-git-0.152.2

RUN git config --global --add safe.directory /app

# Copia i file del progetto nella directory /app
WORKDIR /app
COPY . .

# Espone la porta per il server Hugo
EXPOSE 1313

# Comando per avviare il server di sviluppo Hugo
CMD ["hugo", "server", "--disableFastRender", "--bind", "0.0.0.0"]
