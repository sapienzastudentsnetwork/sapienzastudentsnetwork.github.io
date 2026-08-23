FROM hugomods/hugo:dart-sass-git-0.161.1

RUN apk add --no-cache nodejs npm python3

RUN git config --global --add safe.directory /app

# Copia i file del progetto nella directory /app
WORKDIR /app
COPY . .

# Install npm dependencies and build Tailwind CSS
RUN npm install && npm run build

# Optionally generate source-aware metadata after local volumes are mounted.
COPY _scripts/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Espone la porta per il server Hugo
EXPOSE 1313

# Comando per avviare il server di sviluppo Hugo
CMD ["hugo", "server", "--disableFastRender", "--bind", "0.0.0.0"]
